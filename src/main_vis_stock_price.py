import zmq
import json
import time
import signal
import threading

from collections import deque

import matplotlib.pyplot as plt
import matplotlib.animation as animation

from parsers.exchange_messages import event_topic

interrupted = False

STOCK = "BABA"

CHART_UPDATE_MS = 1000


class PriceHistory:
    def __init__(self, history_len_sec=30):
        self._lock = threading.Lock()
        self._last_trade_prices = deque()
        self._last_trade_ts = deque()
        self._history_len_sec = history_len_sec

    def update(self, events):
        total_trade_amt = 0
        total_trade_qty = 0

        for event in events:
            if event["type"] == "TRADE":
                total_trade_amt += float(event["px"]) * int(event["qty"])
                total_trade_qty += int(event["qty"])
        if total_trade_qty > 0:
            with self._lock:
                ts = time.time()
                self._last_trade_ts.append(ts)
                self._last_trade_prices.append(total_trade_amt / total_trade_qty)

                while (
                    len(self._last_trade_ts) > 0
                    and ts - self._last_trade_ts[0] > self._history_len_sec
                ):
                    self._last_trade_ts.popleft()
                    self._last_trade_prices.popleft()
        # print(f"traded = {total_trade_amt} {total_trade_qty}")

    def get_history(self):
        with self._lock:
            return self._last_trade_prices.copy(), self._last_trade_ts.copy()


def updater_func(ax, pxhistory):
    def update_plot(i):
        px, ts = pxhistory.get_history()

        ax.clear()
        ax.set_ylabel("px")
        ax.set_xlabel("timestamp")
        ax.plot(ts, px)

    return update_plot


def signal_handler(signum, frame):
    global interrupted
    interrupted = True
    exit(1)


def event_handler(psocket, pxhistory):
    while not interrupted:
        try:
            message = psocket.recv(zmq.NOBLOCK)
            # print(message, flush=True)
            topic, events_str = message.split(b" ", 1)
            events = json.loads(events_str)
            pxhistory.update(events["executed"])
        except zmq.ZMQError:
            time.sleep(0.01)


signal.signal(signal.SIGINT, signal_handler)

# events
pcontext = zmq.Context()
psocket = pcontext.socket(zmq.SUB)
psocket.connect("tcp://localhost:10001")
# psocket.subscribe("")
psocket.subscribe(event_topic(STOCK))

fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)
pxhistory = PriceHistory()

th = threading.Thread(
    target=event_handler,
    args=(
        psocket,
        pxhistory,
    ),
)
th.start()

ani = animation.FuncAnimation(
    fig, updater_func(ax1, pxhistory), interval=CHART_UPDATE_MS
)
plt.show()
