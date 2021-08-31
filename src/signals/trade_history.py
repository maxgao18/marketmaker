import time

from collections import deque, defaultdict

from signals.signal import Signal


class TradeHistory(Signal):
    def __init__(self, history_len_sec=10):
        self._prices = defaultdict(deque)
        self._timestamps = defaultdict(deque)
        self._volumes = defaultdict(deque)
        self._history_len_sec = history_len_sec

    def process_exchange_events(self, symbol, events):
        ts = time.time()
        total_trade_amt = defaultdict(lambda: 0)
        total_trade_qty = defaultdict(lambda: 0)

        for event in events["executed"]:
            if event["type"] == "TRADE":
                stock = event["symbol"]
                total_trade_amt[stock] += float(event["px"]) * int(event["qty"])
                total_trade_qty[stock] += int(event["qty"])
        for s, amt in total_trade_amt.items():
            qty = total_trade_qty[s]
            tss = self._timestamps[s]
            qtys = self._volumes[s]
            pxs = self._prices[s]
            tss.append(ts)
            pxs.append(amt / qty)
            qtys.append(int(qty / 2))

            while len(tss) > 0 and ts - tss[0] > self._history_len_sec:
                tss.popleft()
                qtys.popleft()
                pxs.popleft()

    def prices(self, symbol):
        return self._prices[symbol]

    def timestamps(self, symbol):
        return self._timestamps[symbol]

    def volumes(self, symbol):
        return self._volumes[symbol]

    def last_trade_price(self, symbol):
        pxs = self._prices.get(symbol)
        return pxs[0] if pxs is not None and len(pxs) > 0 else None

    def last_trade_volume(self, symbol):
        amts = self._volumes.get(symbol)
        return amts[0] if amts is not None and len(amts) > 0 else None
