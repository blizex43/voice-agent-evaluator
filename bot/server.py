import threading
import uvicorn
import time
from pyngrok import ngrok
from enums.collections import credentials


def start_uvicorn_server_in_thread(
    host: str, port: int
) -> tuple[uvicorn.Server, threading.Thread]:
    """Start the FastAPI webhook app in a background thread so it can run alongside the caller."""
    config = uvicorn.Config("bot.webhook:app", host=host, port=port, reload=False)
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    deadline = time.time() + 5
    while not server.started and thread.is_alive() and time.time() < deadline:
        time.sleep(0.1)
    return server, thread


def quick_run_uvicorn_server(host: str, port: int) -> None:
    """Run the webhook server in the foreground for local development."""
    uvicorn.run("bot.webhook:app", host=host, port=port, reload=False)


def setup_ngrok(auth: str) -> None:
    """Configure the Ngrok authentication token for exposing the local webhook."""
    ngrok.set_auth_token(auth)


def start_ngrok_server(port: int = 8000):
    """Open an Ngrok tunnel so Twilio can reach the local webhook endpoint."""
    tunnel = ngrok.connect(port)
    return tunnel


def indefinitely_serve():
    """Keep the process alive while the server is running in the background."""
    while True:
        time.sleep(1)


def serve_servers(host: str, port: int, pause: bool = False):
    """Set up the webhook server and public tunnel for live Twilio testing."""
    setup_ngrok(credentials["ngrok"]["auth_token"])
    tunnel = start_ngrok_server(port=port)
    server, thread = start_uvicorn_server_in_thread(host, port)
    if pause:
        indefinitely_serve()
    return tunnel, server, thread
