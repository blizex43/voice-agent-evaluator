from threading import Event
from pyee import EventEmitter

call_signal = EventEmitter()
call_ended_event = Event()
recording_saved_event = Event()
parser_signal = EventEmitter()