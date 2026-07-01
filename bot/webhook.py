from fastapi import FastAPI, Request
from fastapi.responses import Response
from urllib.parse import parse_qs
from .analyzer import save_bug_report
from .conversation import Conversation
from .recorder import download_recording_audio, save_recording_metadata
from .transcript import save_transcript
from .caller import Caller
from enums.scenarios import get_scenario, scenario_to_messages
from enums.voice import media_type, call_statuses, voice_choices, languages
from .listeners import parser_signal
from .parser import resolve_parser_reply, parse_value
from typing import Literal
from structs.parser import ParserFunctionNamesType
from twilio.twiml.voice_response import VoiceResponse

app = FastAPI()

conversations: dict[str, Conversation] = {}
caller_instance = Caller()


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "pretty-good-ai-voice-bot",
        "webhooks": {
            "voice": "POST /voice",
            "call_status": "POST /call-status",
            "recording_status": "POST /recording-status",
        },
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@parser_signal.on("parser_succeeded")
def handle_parser_signal_on_receive(
    parser_name: ParserFunctionNamesType, input: str
) -> None:
    """Handle parser success signals on the receiving end (webhook)"""
    if parser_name == "parser_end_call":
        print(f"Received parser_end_call signal: {input}")


async def parse_twilio_form(request: Request) -> dict[str, str]:
    body = (await request.body()).decode("utf-8")
    parsed = parse_qs(body)
    return {key: values[0] for key, values in parsed.items() if values}


@app.post("/voice")
async def voice_webhook(request: Request):
    """
    Twilio will hit this endpoint during a call.
    """
    print("Pre Form Parse")
    form = await parse_twilio_form(request)
    call_sid = form.get("CallSid", "local-test-call")
    user_input = form.get("SpeechResult", "")  # Twilio speech input

    conversation = conversations.get(call_sid)
    if conversation is None:
        scenario = get_scenario("random")
        conversation = Conversation(
            scenario_to_messages(scenario),
            session_id=call_sid,
            metadata={"call_sid": call_sid, "scenario": scenario},
        )
        conversations[call_sid] = conversation
    print("Pre Patient Reply")
    reply = conversation.handle_patient_message(user_input or "Hello")
    print("Post Patient Reply")
    save_transcript(call_sid, conversation.history, conversation.metadata)
    save_bug_report(call_sid, conversation.history)
    print("Pre-resolve")
    parsed_say = parse_value(reply, "parser_say")
    parsed_end = parse_value(reply, "parser_end_call")

    reply_text = parsed_say[0] if parsed_say else reply
    hang_up = parsed_end is not None

    voice_response = append_reply_to_voice_response(reply=reply_text, hang_up=hang_up)
    print(reply, voice_response.to_xml())
    return Response(
        content=voice_response.to_xml(), media_type=media_type, status_code=200
    )


@app.post("/call-status")
async def call_status_webhook(request: Request):
    form = await parse_twilio_form(request)
    call_sid = form.get("CallSid", "local-test-call")
    call_status = form.get("CallStatus", "")
    conversation = conversations.get(call_sid)

    if conversation is not None:
        conversation.metadata["call_status"] = call_status
        save_transcript(call_sid, conversation.history, conversation.metadata)
        save_bug_report(call_sid, conversation.history)

        if call_status in call_statuses:
            conversations.pop(call_sid, None)

    return Response(content="<Response />", media_type=media_type)


@app.post("/recording-status")
async def recording_status_webhook(request: Request):
    form = await parse_twilio_form(request)
    save_recording_metadata(form)

    if form.get("RecordingStatus") == "completed":
        try:
            download_recording_audio(form)
        except Exception as exc:
            form["download_error"] = str(exc)
            save_recording_metadata(form)

    return Response(content="<Response />", media_type=media_type)


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
        action="/voice",
        method="POST",
        timeout=timeout,
        speech_timeout=speech_timeout,
    )
    else: 
        voice_response.hangup()
    return voice_response
