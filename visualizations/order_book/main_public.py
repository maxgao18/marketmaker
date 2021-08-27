import zmq
import json
import time
import signal

from asciimatics.screen import ManagedScreen

from ascii_gui import ScreenState

interrupted = False

STOCK = "BABA"
_BOOK_TOPIC_FORMAT = f"book::{STOCK}"


def signal_handler(signum, frame):
    global interrupted
    interrupted = True


signal.signal(signal.SIGINT, signal_handler)

# events
pcontext = zmq.Context()
psocket = pcontext.socket(zmq.SUB)
psocket.connect("tcp://localhost:10001")
psocket.subscribe(_BOOK_TOPIC_FORMAT)

with ManagedScreen() as screen:
    ss = ScreenState(screen, STOCK)
    ss.update({"bids": {}, "asks": {}})
    while not interrupted:
        try:
            message = psocket.recv(zmq.NOBLOCK)
            topic, book_str = message.split(b" ", 1)
            book = json.loads(book_str)
            ss.update(book)
        except zmq.ZMQError:
            time.sleep(0.01)
