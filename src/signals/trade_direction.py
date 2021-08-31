import time
import numpy as np

from collections import deque, defaultdict

from signals.signal import Signal


class TradeDirection(Signal):
    """
    -1 means aggressor was a likely a seller
    1 means aggressor was a likely a buyer

    Uses the tick rule

    b_{t} = b_{t-1} if delta(px) == 0 else sign(delta(px))
    """

    def __init__(self, history_len_sec=120):
        self._aggressor = defaultdict(deque)
        self._volumes = defaultdict(deque)
        self._prices = defaultdict(deque)
        self._timestamps = defaultdict(deque)
        self._history_len_sec = history_len_sec

    def process_exchange_events(self, symbol, events):
        ts = time.time()

        trades = [
            (event["qty"], event["px"])
            for event in events["executed"]
            if event["type"] == "TRADE"
        ]
        if len(trades) == 0:
            return

        qty, px = sorted(trades)[-1]

        aggs = self._aggressor[symbol]
        pxs = self._prices[symbol]
        vols = self._volumes[symbol]
        tss = self._timestamps[symbol]

        dpx = px - pxs[-1] if len(pxs) > 0 else px
        if dpx != 0:
            agg = np.sign(dpx)
        else:
            agg = 1 if len(aggs) == 0 else aggs[-1]
        aggs.append(agg)
        pxs.append(px)
        vols.append(qty)
        tss.append(ts)

        while len(tss) > 0 and ts - tss[0] > self._history_len_sec:
            aggs.popleft()
            tss.popleft()
            vols.popleft()
            pxs.popleft()

    def prices(self, symbol):
        return self._prices.get(symbol)

    def timestamps(self, symbol):
        return self._timestamps.get(symbol)

    def volumes(self, symbol):
        return self._volumes.get(symbol)

    def directions(self, symbol):
        return self._aggressor.get(symbol)
