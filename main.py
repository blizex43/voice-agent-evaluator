
from bot.server import (
    serve_servers,
    indefinitely_serve
)
from bot.caller import place_call
from bot.config import validate_config
from enums.dir import OUTPUT_DIR, RECORDING_DIR, REPORT_DIR, TRANSCRIPT_DIR
from util.cmds import build_parser
def ensure_output_dirs() -> None:
    for directory in [OUTPUT_DIR, RECORDING_DIR, REPORT_DIR, TRANSCRIPT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

def run_server_and_call(host: str, port: int = 8000) -> None:
    validate_config(require_twilio=True)
    tunnel = serve_servers(host, port)[0]
    try:
        place_call(tunnel.public_url)
    except KeyboardInterrupt:
        print("Stopping server after keyboard interrupt...")
    finally:
        indefinitely_serve()

def validate_environment(require_twilio: bool) -> None:
    validate_config(require_twilio=require_twilio)
    print("Environment looks good.")


def main() -> None:
    ensure_output_dirs()
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "serve":
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
