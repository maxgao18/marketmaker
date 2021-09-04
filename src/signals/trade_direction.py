import time
import numpy as np

from collections import deque, defaultdict

from utils.sliding_window import SlidingWindow
from utils.algorithms import largest_trade
from signals.signal import Signal


class TradeDirection(Signal):
    """
    -1 means aggressor was a likely a seller
    1 means aggressor was a likely a buyer

    Uses the tick rule

    b_{t} = b_{t-1} if delta(px) == 0 else sign(delta(px))
    """

    def __init__(self, history_len_sec=120):
        self._aggressor = defaultdict(lambda: SlidingWindow(history_len_sec))
        self._volumes = defaultdict(lambda: SlidingWindow(history_len_sec))
        self._prices = defaultdict(lambda: SlidingWindow(history_len_sec))
        self._timestamps = defaultdict(lambda: SlidingWindow(history_len_sec))
        self._history_len_sec = history_len_sec

    def process_exchange_events(self, symbol, events):
        ts = time.time()

        trade = largest_trade(events)
        if trade is None:
            return

        qty, px = trade["qty"], trade["px"]

        aggs = self._aggressor[symbol]
        pxs = self._prices[symbol]
        vols = self._volumes[symbol]
        tss = self._timestamps[symbol]

        dpx = px - pxs[-1] if len(pxs) > 0 else px
        if dpx != 0:
            agg = np.sign(dpx)
        else:
            agg = 1 if len(aggs) == 0 else aggs[-1]
        aggs.append(agg, ts)
        pxs.append(px, ts)
        vols.append(qty, ts)
        tss.append(ts, ts)

    def prices(self, symbol):
        if symbol not in self._prices:
            return None

        return self._prices.get(symbol).values

    def timestamps(self, symbol):
        if symbol not in self._timestamps:
            return None

        return self._timestamps.get(symbol).values

    def volumes(self, symbol):
        if symbol not in self._volumes:
            return None

        return self._volumes.get(symbol).values

    def directions(self, symbol):
        if symbol not in self._aggressor:
            return None

        return self._aggressor.get(symbol).values
