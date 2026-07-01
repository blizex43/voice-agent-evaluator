import threading
from pyee import EventEmitter

call_signal = EventEmitter()
call_ended_event = threading.Event()
parser_signal = EventEmitter()