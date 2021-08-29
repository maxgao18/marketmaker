import time
import random

import numpy as np

from agents.trader import Trader
from utils.trade import cancel_all, cancel, market, limit, Side


def _idx_of_next_largest_backwards_search(lst, v):
    if lst is None or len(lst) == 0:
        return -1
    if lst[0] > v:
        return 0

    for i in range(1, len(lst) + 1):
        if lst[-i] <= v:
            return len(lst) + 1 - i
    return -1


def _recalculate_theo(c_theo, trade_hist, since_ts, symbol, volume_scale=20):
    pxs = trade_hist.last_trade_pxs(symbol)
    tss = trade_hist.last_trade_tss(symbol)
    volumes = trade_hist.last_trade_volumes(symbol)

    idx = _idx_of_next_largest_backwards_search(tss, since_ts)
    if idx < 0:
        return c_theo

    for i in range(idx, len(tss)):
        if c_theo is None:
            c_theo = pxs[i]

        diff = pxs[i] - c_theo
        c_theo += min(1, volumes[i] / volume_scale) * diff

    return c_theo


class MarketMaker(Trader):
    def __init__(self, max_position, stock, half_spread=0.05, **kwargs):
        super().__init__(**kwargs)
        self._max_position = max_position
        self._half_spread = half_spread
        self._stock = stock

        self._stock_theo = 1
        self._last_timestamp = 0

        self._last_refresh = 0
        self._refresh_period = 4

        self._last_print = 0

    def callback_options(self):
        return Trader.CallBackOptions(always_run=False, on_event=True)

    def symbols(self):
        return set([self._stock])

    def init(self, state):
        self.submit_to_exchange(state, func=cancel_all, symbol="*")
        self._last_refresh = time.time()

    def run(self, state):
        ts = time.time()

        new_theo = _recalculate_theo(
            self._stock_theo, state.trade_history, self._last_timestamp, self._stock
        )

        outstanding_orders = state.portfolio.outstanding_orders(self._stock)
        in_flight_orders = state.portfolio.in_flight_orders(self._stock)
        stock_position = state.portfolio.holding(self._stock)

        if (self._stock_theo is not None and abs(new_theo - self._stock_theo)) or (
            ts - self._last_refresh > self._refresh_period
        ):
            self.submit_to_exchange(state, func=cancel_all, symbol=self._stock)
            self._last_refresh = ts
        elif new_theo is not None:
            out_bid_qty = 0
            out_ask_qty = 0
            for lst in [outstanding_orders.values(), in_flight_orders.values()]:
                for o in lst:
                    otype = o.get("type")
                    if otype == "LIMIT" or otype == "MARKET" or otype == "ADD":
                        if o["side"] == Side.BUY:
                            out_bid_qty += o["qty"]
                        else:
                            out_ask_qty += o["qty"]
            additional_ask_edge = (
                -stock_position / self._max_position * self._half_spread
            )
            additional_bid_edge = -additional_ask_edge
            bid_px = np.round(new_theo - self._half_spread - additional_bid_edge, 2)
            ask_px = np.round(new_theo + self._half_spread + additional_ask_edge, 2)

            bid_qty = self._max_position - stock_position - out_bid_qty
            ask_qty = self._max_position + stock_position - out_ask_qty

            if ts - self._last_print > 0.5:
                print("================================")
                print(f"holding - {state.portfolio.holdings()}")
                print(f"bv - {state.portfolio.book_values()}")
                print(f"pv - {sum(state.portfolio.book_values().values())}", flush=True)
                print(f"theo - {new_theo}")
                print(f"ba {bid_px} - {ask_px}", flush=True)
                print(outstanding_orders)
                print(in_flight_orders)
                self._last_print = ts

            if bid_qty > 0:
                self.submit_to_exchange(
                    state,
                    func=limit,
                    symbol=self._stock,
                    qty=bid_qty,
                    px=bid_px,
                    side=Side.BUY,
                )
            if ask_qty > 0:
                self.submit_to_exchange(
                    state,
                    func=limit,
                    symbol=self._stock,
                    qty=ask_qty,
                    px=ask_px,
                    side=Side.SELL,
                )

        self._stock_theo = new_theo
        self._last_timestamp = ts


if __name__ == "__main__":
    print(_idx_of_next_largest_backwards_search([1, 2, 3], 3))
    print(_idx_of_next_largest_backwards_search([1, 2, 3], 1))
    print(_idx_of_next_largest_backwards_search([1, 2, 3], 0))
    print(_idx_of_next_largest_backwards_search([1, 2, 3], 4))
