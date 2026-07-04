from argparse import ArgumentParser
from enums.scenarios import scenario_names
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
