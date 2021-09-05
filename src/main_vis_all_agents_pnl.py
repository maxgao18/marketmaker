from collections import defaultdict
import traceback
import zmq
import time
import signal
import threading

import matplotlib.pyplot as plt
import matplotlib.animation as animation

from management.portfolio import Portfolio
from management.order_book import OrderBooks
from agents.trader import Trader
from utils.state import State
from utils.exchange_messages import split_topic, parse_book_str, parse_event_str
from utils.sliding_window import SlidingWindow

CHART_UPDATE_MS = 1000
HISTORY_LEN_SEC = -1


def signal_handler(signum, frame):
    exit(1)


class DummyTrader(Trader):
    def symbols(self):
        pass

    def init(self, state):
        pass

    def run(self, state):
        pass


def run(psub_addr, portfolios, traders):
    states = {}
    order_book = OrderBooks()

    pcontext = zmq.Context()
    psocket = pcontext.socket(zmq.SUB)
    psocket.connect(psub_addr)
    psocket.subscribe("")

    while True:
        while True:
            try:
                message = psocket.recv(zmq.NOBLOCK)
                # print(message, flush=True)

                topic, body = message.split(b" ", 1)
                msg_type, symbol = split_topic(topic)

                if msg_type == "book":
                    books = parse_book_str(body)
                    order_book.process_exchange_books(symbol, books)
                elif msg_type == "event":
                    events = parse_event_str(body)
                    for lst in events.values():
                        for e in lst:
                            user = e.get("user")
                            if user is not None and user not in traders:
                                traders[user] = DummyTrader(user=user)
                                portfolios[user] = Portfolio(user=user)
                                states[user] = State(portfolios[user], None, order_book)

                    for p in portfolios.values():
                        p.process_exchange_events(events)
                else:
                    continue

                for u, t in traders.items():
                    t.set_pnls(states[u])

            except zmq.ZMQError:
                time.sleep(0.01)


def updater_func(ax, portfolio, traders, history_len_sec):
    user_to_pnl = defaultdict(lambda: SlidingWindow(history_len_sec))

    def update_plot(i):
        ts = time.time()
        ax.clear()
        for u, t in traders.items():
            window = user_to_pnl[u]
            window.append(t.realized_pnl + t.unrealized_pnl, ts)
            ax.plot(window.indexes, window.values, label=u)
        ax.set_title("P/L for all users")
        ax.set_ylabel("P/L")
        ax.set_xlabel("Timestamp")
        ax.legend()

    return update_plot


signal.signal(signal.SIGINT, signal_handler)


fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)

portfolios = {}
traders = {}

th = threading.Thread(
    target=run,
    args=(
        "tcp://localhost:10001",
        portfolios,
        traders,
    ),
)
th.setDaemon(True)
th.start()

ani = animation.FuncAnimation(
    fig,
    updater_func(ax1, portfolios, traders, HISTORY_LEN_SEC),
    interval=CHART_UPDATE_MS,
)
plt.show()
