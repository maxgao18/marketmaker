import zmq
import json
import time
import signal

from asciimatics.screen import ManagedScreen

from parsers.exchange_messages import book_topic, parse_book_str
from visualizations.order_book.ascii_gui import ScreenState

interrupted = False

STOCK = "BABA"
MAX_FPS = 0

period = 0 if MAX_FPS == 0 else 1 / MAX_FPS


def signal_handler(signum, frame):
    exit(1)


signal.signal(signal.SIGINT, signal_handler)

# events
pcontext = zmq.Context()
psocket = pcontext.socket(zmq.SUB)
psocket.connect("tcp://localhost:10001")
psocket.subscribe(book_topic(STOCK))

last_update = 0
with ManagedScreen() as screen:
    ss = ScreenState(screen, STOCK)
    ss.update({"bids": {}, "asks": {}})
    while not interrupted:
        try:
            message = psocket.recv(zmq.NOBLOCK)
            topic, book_str = message.split(b" ", 1)
            book = parse_book_str(book_str)
            if time.time() - last_update > period:
                ss.update(book, hist_len=30)
                last_update = time.time()
        except zmq.ZMQError:
            time.sleep(0.01)
