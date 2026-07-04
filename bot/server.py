import threading
import uvicorn
import time
from pyngrok import ngrok
def start_uvicorn_server_in_thread(
    host: str, port: int
) -> tuple[uvicorn.Server, threading.Thread]:
    config = uvicorn.Config("bot.webhook:app", host=host, port=port, reload=False)
    server = uvicorn.Server(config)
    
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    deadline = time.time() + 5
    while not server.started and thread.is_alive() and time.time() < deadline:
        time.sleep(0.1)
    return server, thread

def quick_run_uvicorn_server(host: str, port: int) -> None:
    uvicorn.run("bot.webhook:app", host=host, port=port, reload=False)

def setup_ngrok(auth: str) -> None:
    ngrok.set_auth_token(auth)

def start_ngrok_server(port: int = 8000):
    tunnel = ngrok.connect(port)
    return tunnel
def indefinitely_serve():
    while True:
        time.sleep(1)