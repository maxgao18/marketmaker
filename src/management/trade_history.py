import time

from collections import deque, defaultdict


class TradeHistory:
    def __init__(self, history_len_sec=10):
        self._last_trade_prices = defaultdict(deque)
        self._last_trade_ts = defaultdict(deque)
        self._last_trade_volumes = defaultdict(deque)
        self._history_len_sec = history_len_sec

    def process_exchange_events(self, events):
        ts = time.time()
        total_trade_amt = defaultdict(lambda: 0)
        total_trade_qty = defaultdict(lambda: 0)

        for event in events:
            if event["type"] == "TRADE":
                stock = event["stock"]
                total_trade_amt[stock] += float(event["px"]) * int(event["qty"])
                total_trade_qty[stock] += int(event["qty"])
        for s, amt in total_trade_amt.items():
            qty = total_trade_qty[s]
            tss = self._last_trade_ts[s]
            qtys = self._last_trade_volumes[s]
            pxs = self._last_trade_prices[s]
            tss.append(ts)
            pxs.append(amt / qty)
            qtys.append(int(qty / 2))

            while len(tss) > 0 and ts - tss[0] > self._history_len_sec:
                tss.popleft()
                qtys.popleft()
                pxs.popleft()

    def last_trade_px(self, symbol):
        pxs = self._last_trade_prices.get(symbol)
        return pxs[0] if len(pxs) > 0 else None

    def last_trade_volume(self, symbol):
        amts = self._last_trade_volumes.get(symbol)
        return amts[0] if len(amts) > 0 else None
