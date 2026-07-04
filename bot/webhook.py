from fastapi import FastAPI, Request
from fastapi.responses import Response
from urllib.parse import parse_qs
from .analyzer import save_bug_report
from .conversation import Conversation
from .recorder import download_recording_audio, save_recording_metadata
from .transcript import save_transcript
from .caller import Caller
from enums.scenarios import get_scenario, scenario_to_messages
from enums.voice import call_statuses, voice_choices, languages
from enums.logger import log_and_raise, log_info
from enums.strings import (
    DEFAULT_CALL_SID,
    DEFAULT_USER_INPUT,
    EMPTY_TWIML,
    MEDIA_TYPE,
    RECORDING_STATUS_COMPLETED,
    SERVICE_NAME,
    WEBHOOK_CALL_STATUS_PATH,
    WEBHOOK_HEALTH_PATH,
    WEBHOOK_RECORDING_STATUS_PATH,
    WEBHOOK_VOICE_PATH,
)
from .listeners import parser_signal
from .parser import resolve_parser_reply
from typing import Literal
from structs.parser import ParserFunctionNamesType
from structs.prompts import ScenarioNamesType, Scenario
from structs.custom import Maybe
from twilio.twiml.voice_response import VoiceResponse

app = FastAPI()
conversations: dict[str, Conversation] = {}
caller_instance = Caller()


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "webhooks": {
            "voice": "POST " + WEBHOOK_VOICE_PATH,
            "call_status": "POST " + WEBHOOK_CALL_STATUS_PATH,
            "recording_status": "POST " + WEBHOOK_RECORDING_STATUS_PATH,
        },
    }


@app.get(WEBHOOK_HEALTH_PATH)
async def health() -> dict[str, str]:
    return {"status": "ok"}


@parser_signal.on("parser_succeeded")
def handle_parser_signal_on_receive(
    parser_name: ParserFunctionNamesType, input: str
) -> None:
    """Handle parser success signals on the receiving end (webhook)"""
    if parser_name == "parser_end_call":
        log_info(f"Received parser_end_call signal: {input}")


async def parse_twilio_form(request: Request) -> dict[str, str]:
    body = (await request.body()).decode("utf-8")
    parsed = parse_qs(body)
    return {key: values[0] for key, values in parsed.items() if values}


def _resolve_speech_text_and_hangup(reply: str) -> tuple[str, bool]:
    """Use resolve_parser_reply to extract speech text and hang-up flag from a reply."""
    text, should_end = resolve_parser_reply(reply)
    return text, should_end


def get_generated_conversation(
    sid: str, scenario_type: ScenarioNamesType | Literal["random"] = "random"
) -> Conversation:
    scenario = get_scenario(scenario_type)
    conversation = Conversation(
        scenario_to_messages(scenario),
        session_id=sid,
        metadata={"call_sid": sid, "scenario": scenario},
    )
    conversations[sid] = conversation
    return conversation


async def save_history_to_file_async(sid: str, conversation: Conversation) -> None:
    save_transcript(sid, conversation.history, conversation.metadata, conversation.id)
    save_bug_report(sid, conversation.history, conversation.id)


def append_reply_to_voice_response(
    reply: str,
    voice_index: int = 4,
    timeout: int | Literal["auto"] = 60,
    speech_timeout: int | Literal["auto"] = 0.8,
    language_index: int = 0,
    hang_up: bool = False,
) -> VoiceResponse:
    voice_response = VoiceResponse()
    voice_response.say(
        reply, voice=voice_choices[voice_index], language=languages[language_index]
    )
    if not hang_up:
        voice_response.gather(
            input="speech",
            action=WEBHOOK_VOICE_PATH,
            method="POST",
            timeout=timeout,
            speech_timeout=speech_timeout,
        )
    else:
        voice_response.hangup()
    return voice_response


@app.post(WEBHOOK_VOICE_PATH)
async def voice_webhook(request: Request):
    """
    Twilio will hit this endpoint during a call.
    """
    form = await parse_twilio_form(request)
    call_sid = form.get("CallSid", DEFAULT_CALL_SID)
    user_input = form.get("SpeechResult", "")
    conversation = conversations.get(call_sid) or get_generated_conversation(
        call_sid, "random"
    )
    scenario: Maybe[Scenario] = conversation.metadata.get("scenario")
    if ((not DEFAULT_USER_INPUT) and (not user_input) and (conversation.metadata.get("call_status") == None)):
        return Response(content=append_reply_to_voice_response("").to_xml(), media_type=MEDIA_TYPE, status_code=200)

    reply = await conversation.handle_user_message(user_input or DEFAULT_USER_INPUT)
    reply_text, hang_up = _resolve_speech_text_and_hangup(reply)
    await save_history_to_file_async(call_sid, conversation)
    voice_response = append_reply_to_voice_response(reply=reply_text, hang_up=hang_up, voice_index=scenario.patient.voice_index if scenario is not None else None)
    log_info(f"input={user_input} reply={reply!r} reply_text={reply_text!r} hang_up={hang_up}")
    return Response(
        content=voice_response.to_xml(), media_type=MEDIA_TYPE, status_code=200
    )


@app.post(WEBHOOK_CALL_STATUS_PATH)
async def call_status_webhook(request: Request):
    form = await parse_twilio_form(request)
    call_sid = form.get("CallSid", DEFAULT_CALL_SID)
    call_status = form.get("CallStatus", "")
    conversation = conversations.get(call_sid) or get_generated_conversation(
        call_sid, "random"
    )

    if conversation is not None:
        conversation.metadata["call_status"] = call_status
        save_transcript(call_sid, conversation.history, conversation.metadata, conversation.id)
        save_bug_report(call_sid, conversation.history, conversation.id)

    return Response(content=EMPTY_TWIML, media_type=MEDIA_TYPE)


@app.post(WEBHOOK_RECORDING_STATUS_PATH)
async def recording_status_webhook(request: Request):
    form = await parse_twilio_form(request)
    call_sid = form.get("CallSid", DEFAULT_CALL_SID)
    call_status = form.get("CallStatus", "")
    conversation = conversations.get(call_sid) or get_generated_conversation(
        call_sid, "random"
    ) 
    save_recording_metadata(form, conversation)
    if form.get("RecordingStatus") == RECORDING_STATUS_COMPLETED:
        try:
            download_recording_audio(form, conversation)
        except Exception as exc:
            form["download_error"] = str(exc)
            save_recording_metadata(form, conversation)
            log_and_raise(
                exc,
                f"Failed to download recording audio! Download Error: {form['download_error']} SID: {call_sid}",
            )
    if call_status in call_statuses:
            conversations.pop(call_sid, None)

    return Response(content=EMPTY_TWIML, media_type=MEDIA_TYPE)
