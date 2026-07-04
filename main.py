from argparse import ArgumentParser
from uuid import uuid4
from bot.server import (
    start_uvicorn_server_in_thread,
    start_ngrok_server,
    setup_ngrok,
    indefinitely_serve
)
from bot.analyzer import save_bug_report
from bot.caller import Caller
from bot.config import validate_config
from bot.conversation import Conversation
from bot.listeners import call_signal, call_ended_event
from bot.transcript import save_transcript
from enums.dir import OUTPUT_DIR, RECORDING_DIR, REPORT_DIR, TRANSCRIPT_DIR
from enums.scenarios import scenario_names, get_scenario, scenario_to_messages
from enums.strings import SIMULATION_SESSION_PREFIX
from structs.prompts import ScenarioNamesType
from enums.collections import credentials

def ensure_output_dirs() -> None:
    for directory in [OUTPUT_DIR, RECORDING_DIR, REPORT_DIR, TRANSCRIPT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def build_simulation_session_id(scenario_name: ScenarioNamesType) -> str:
    """Compose a unique session id for a simulation run."""
    return f"{SIMULATION_SESSION_PREFIX}{scenario_name}-{uuid4().hex[:8]}"


def run_simulation(scenario_name: ScenarioNamesType) -> None:
    validate_config(require_twilio=False)
    ensure_output_dirs()

    scenario = get_scenario(scenario_name)
    session_id = build_simulation_session_id(scenario_name)
    conversation = Conversation(
        scenario_to_messages(scenario),
        session_id=session_id,
        metadata={"mode": "simulation", "scenario": scenario},
    )

    conversation.run()
    transcript_paths = save_transcript(
        session_id, conversation.history, conversation.metadata, conversation.id
    )
    report_paths = save_bug_report(session_id, conversation.history, conversation.id)

    print(f"Transcript: {transcript_paths['md']}")
    print(f"Bug report: {report_paths['md']}")


def serve_servers(host: str, port: int, pause: bool = False):
    setup_ngrok(credentials["ngrok"]["auth_token"])
    tunnel = start_ngrok_server(port=port)
    server, thread = start_uvicorn_server_in_thread(host, port)
    if pause: 
        indefinitely_serve()
    return tunnel, server, thread


def run_server_and_call(host: str, port: int = 8000) -> None:
    validate_config(require_twilio=True)
    tunnel, server, thread = serve_servers(host, port)
    try:
        place_call(tunnel.public_url)
    except KeyboardInterrupt:
        print("Stopping server after keyboard interrupt...")
    finally:
        indefinitely_serve()
        
            


def place_call(http: str = None) -> None:
    validate_config(require_twilio=True)

    call_ended_event.clear()

    def on_call_ended(call_sid: str, status: str) -> None:
        print(f"Received call.ended event: {call_sid} status={status}")

    call_signal.once("call.ended", on_call_ended)

    caller = Caller()
    call_sid = caller.make_call(http)
    print(f"Waiting for call to end for {call_sid}...")
    call_ended_event.wait()
    print(f"Call process ending after call.ended for {call_sid}")


def validate_environment(require_twilio: bool) -> None:
    validate_config(require_twilio=require_twilio)
    print("Environment looks good.")


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Pretty Good AI voice bot runner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    simulate = subparsers.add_parser("simulate", help="Run a scripted patient scenario")
    simulate.add_argument(
        "--scenario",
        choices=sorted(scenario_names),
        default="refill",
        help="Scenario to run",
    )

    serve = subparsers.add_parser("serve", help="Start the FastAPI webhook server")
    serve.add_argument("--host", default="0.0.0.0")
    serve.add_argument("--port", type=int, default=8000)

    run = subparsers.add_parser(
        "run",
        help="Start the webhook server and place a Twilio outbound call",
    )
    run.add_argument("--host", default="0.0.0.0")
    run.add_argument("--port", type=int, default=8000)

    subparsers.add_parser("call", help="Place a Twilio outbound call")

    validate = subparsers.add_parser("validate", help="Check required environment")

    validate.add_argument(
        "--twilio",
        action="store_true",
        help="Also require Twilio and NGROK_BACKUP_ENDPOINT_URL settings",
    )

    return parser


def main() -> None:
    ensure_output_dirs()
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "simulate":
        run_simulation(args.scenario)
    elif args.command == "serve":
        serve_servers(args.host, args.port, True)
    elif args.command == "call":
        place_call()
    elif args.command == "run":
        run_server_and_call(args.host, args.port)
    elif args.command == "validate":
        validate_environment(require_twilio=args.twilio)
    else:
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
