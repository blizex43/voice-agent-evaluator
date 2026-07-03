import time
import threading
from twilio.rest import Client
from enums.collections import credentials, urls
from bot.listeners import call_signal, call_ended_event

class Caller:
    def __init__(self):
        self.client = Client(
            credentials["twilio"]["account_sid"], credentials["twilio"]["auth_token"]
        )
        self.from_number = credentials["twilio"]["from_phone_number"]
        self.to_number = credentials["twilio"]["to_phone_number"]
        self.recent_call = None
        self._status_watcher = None
        self._stop_watcher = threading.Event()

    def end_call(self) -> None:
        """End the most recent active call"""
        if self.recent_call:
            call_sid = self.recent_call.sid
            try:
                # Update the call to complete it
                self.client.calls(call_sid).update(status="completed")
                print(f"Call ended: {call_sid}")
            except Exception as e:
                print(f"Error ending call {call_sid}: {e}")

    def _handle_call_completed(self, call_sid: str, status: str) -> None:
        print(f"Call status changed to {status} for {call_sid}")
        call_ended_event.set()
        call_signal.emit("call.ended", call_sid, status)

    def _watch_call_status(self, call_sid: str) -> None:
        while not self._stop_watcher.is_set():
            try:
                call = self.client.calls(call_sid).fetch()
                status = call.status
            except Exception as e:
                print(f"Error fetching call status for {call_sid}: {e}")
                break

            if status in {"completed", "canceled", "failed", "busy", "no-answer"}:
                self._handle_call_completed(call_sid, status)
                break

            time.sleep(2)

    def make_call(self):
        base_url: str = urls["endpoint"]
        voice_url = f"{base_url}/voice"
        call_status_url = f"{base_url}/call-status"
        recording_status_url = f"{base_url}/recording-status"

        call = self.client.calls.create(
            to=self.to_number,
            from_=self.from_number,
            url=voice_url,
            method="POST",
            status_callback=call_status_url,
            status_callback_event=["completed"],
            status_callback_method="POST",
            record=True,
            recording_channels="dual",
            recording_status_callback=recording_status_url,
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
        print(f"Call started: {call.sid}")
        return call.sid
