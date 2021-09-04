import time

from abc import ABC, abstractmethod
from collections import defaultdict, namedtuple

from signals.signal import Signal
from utils.sliding_window import SlidingWindow
from utils.algorithms import largest_trade

Bar = namedtuple(
    "Bar", ["volume", "high", "low", "open", "close", "start_ts", "end_ts"]
)


class WeightedBars(Signal, ABC):
    def __init__(self, thres, history_len_sec=100):
        self._thres = thres
        self._trade_events = defaultdict(list)
        self._start_ts = {}
        self._weight_sum = defaultdict(lambda: 0)
        self._bars = defaultdict(lambda: SlidingWindow(history_len_sec))

    @abstractmethod
    def get_weight(self, trade_event):
        pass

    def process_exchange_events(self, symbol, events, ts=None):
        ts = time.time()

        trade = largest_trade(events)
        if trade is None:
            return

        if len(self._trade_events[symbol]) == 0:
            self._start_ts[symbol] = ts
        self._trade_events[symbol].append(trade)
        self._weight_sum[symbol] += self.get_weight(trade)

        if self._weight_sum[symbol] >= self._thres:
            events = self._trade_events[symbol]
            total_volume = sum(e["qty"] for e in events)
            pxs = [e["px"] for e in events]
            self._bars[symbol].append(
                Bar(
                    volume=total_volume,
                    high=max(pxs),
                    low=min(pxs),
                    open=pxs[0],
                    close=pxs[-1],
                    start_ts=self._start_ts[symbol],
                    end_ts=ts,
                ),
                ts,
            )
            self._trade_events[symbol].clear()
            self._weight_sum[symbol] = 0

    def bars(self, symbol):
        return self._bars.get(symbol, None)


class VolumeBars(WeightedBars):
    def get_weight(self, trade_event):
        return trade_event["qty"]


class DollarBars(WeightedBars):
    def get_weight(self, trade_event):
        return trade_event["qty"] * trade_event["px"]
