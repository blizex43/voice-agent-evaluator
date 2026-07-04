import time
import threading
from twilio.rest import Client
from enums.collections import credentials, urls
from enums.logger import log_info, logger, log_and_raise
from enums.strings import POLL_INTERVAL_SECONDS
from bot.listeners import call_signal, call_ended_event

TERMINAL_CALL_STATUSES = {"completed", "canceled", "failed", "busy", "no-answer"}


class Caller:
    def __init__(self):
        self.client = Client(
            credentials["twilio"]["account_sid"], credentials["twilio"]["auth_token"]
        )
        self.from_number = credentials["twilio"]["from_phone_number"]
        self.to_number = credentials["twilio"]["to_phone_number"]
        print(self.to_number)
        self.recent_call = None
        self._status_watcher = None
        self._stop_watcher = threading.Event()

    def end_call(self) -> None:
        """End the most recent active call"""
        if not self.recent_call:
            return

        call_sid = self.recent_call.sid
        try:
            # Update the call to complete it
            self.client.calls(call_sid).update(status="completed")
            log_info(f"Call ended: {call_sid}")
        except Exception as exc:
            log_and_raise(exc, f"Failed to end call {call_sid}")

    def _handle_call_completed(self, call_sid: str, status: str) -> None:
        log_info(f"Call status changed to {status} for {call_sid}")
        call_ended_event.set()
        call_signal.emit("call.ended", call_sid, status)

    def _fetch_call_status(self, call_sid: str) -> str | None:
        """Fetch the current call status. Returns the status, or None on error."""
        try:
            return self.client.calls(call_sid).fetch().status
        except Exception:
            logger.exception(f"Error fetching call status for {call_sid}")
            return None

    def _watch_call_status(self, call_sid: str) -> None:
        while not self._stop_watcher.is_set():
            status = self._fetch_call_status(call_sid)
            if status is None:
                break

            if status in TERMINAL_CALL_STATUSES:
                self._handle_call_completed(call_sid, status)
                break

            time.sleep(POLL_INTERVAL_SECONDS)

    def _build_callback_urls(self, addr: str) -> dict[str, str]:
        if not addr:
            addr = urls["endpoint"]
        return {
            "voice": f"{addr}/voice",
            "call_status": f"{addr}/call-status",
            "recording_status": f"{addr}/recording-status",
        }

    def make_call(self, addr: str):
        urls_map = self._build_callback_urls(addr)
        call = self.client.calls.create(
            to=self.to_number,
            from_=self.from_number,
            url=urls_map["voice"],
            method="POST",
            status_callback=urls_map["call_status"],
            status_callback_event=["completed"],
            status_callback_method="POST",
            record=True,
            recording_channels="dual",
            recording_status_callback=urls_map["recording_status"],
            recording_status_callback_event=["completed"],
            recording_status_callback_method="POST",
            trim="trim-silence",
        )
        self.recent_call = call
        self._stop_watcher.clear()
        self._status_watcher = threading.Thread(
            target=self._watch_call_status,
            args=(call.sid,),
            daemon=True,
        )
        self._status_watcher.start()
        log_info(f"Call started: {call.sid}")
        return call.sid

def place_call(http: str = None) -> None:
    call_ended_event.clear()
    def on_call_ended(call_sid: str, status: str) -> None:
        print(f"Received call.ended event: {call_sid} status={status}")
    call_signal.once("call.ended", on_call_ended)
    caller = Caller()
    call_sid = caller.make_call(http)
    print(f"Waiting for call to end for {call_sid}...")
    call_ended_event.wait()
    print(f"Call process ending after call.ended for {call_sid}")