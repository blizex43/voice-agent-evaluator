from argparse import ArgumentParser
from uuid import uuid4

import uvicorn
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
        session_id, conversation.history, conversation.metadata
    )
    report_paths = save_bug_report(session_id, conversation.history)

    print(f"Transcript: {transcript_paths['md']}")
    print(f"Bug report: {report_paths['md']}")


def run_server(host: str, port: int) -> None:
    validate_config(require_twilio=False)
    ensure_output_dirs()
    uvicorn.run("bot.webhook:app", host=host, port=port, reload=False)


def place_call() -> None:
    validate_config(require_twilio=True)
    ensure_output_dirs()

    call_ended_event.clear()

    def on_call_ended(call_sid: str, status: str) -> None:
        print(f"Received call.ended event: {call_sid} status={status}")

    call_signal.once("call.ended", on_call_ended)

    caller = Caller()
    call_sid = caller.make_call()
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

    subparsers.add_parser("call", help="Place a Twilio outbound call")

    validate = subparsers.add_parser("validate", help="Check required environment")

    validate.add_argument(
        "--twilio",
        action="store_true",
        help="Also require Twilio and ENDPOINT_URL settings",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "simulate":
        run_simulation(args.scenario)
    elif args.command == "serve":
        run_server(args.host, args.port)
    elif args.command == "call":
        place_call()
    elif args.command == "validate":
        validate_environment(require_twilio=args.twilio)
    else:
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
