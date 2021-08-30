import time
import random

import numpy as np

from agents.trader import Trader
from utils.trade import cancel_all, cancel, market, limit, Side


class InformedTrader(Trader):
    def __init__(
        self,
        arrival_rate,
        stock,
        stock_true_theo,
        qty_min=1,
        qty_max=20,
        qty_inc_from_theo=0.01,
        use_market=False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._arrival_rate = arrival_rate
        self._stock = stock
        self._stock_true_theo = stock_true_theo
        self._qty_max = qty_max
        self._qty_min = qty_min
        self._qty_inc_from_theo = qty_inc_from_theo

        self._period = 1 / arrival_rate
        self._use_market = use_market
        self._next_submit = 0

    def callback_options(self):
        return Trader.CallBackOptions(always_run=True)

    def symbols(self):
        return set([self._stock])

    def init(self, state):
        self.submit_to_exchange(state, func=cancel_all, symbol="*")

    def run(self, state):
        ts = time.time()
        if self._next_submit < ts:
            self.submit_to_exchange(
                state, func=cancel_all, symbol="*"
            )
            print(f"================================{self.user}")
            print(f"holdings - {state.portfolio.holdings()}")
            print(f"bv - {self.book_value}")
            print(f"books - {state.portfolio.book_values()}")
            print(f"pnl - {self.realized_pnl}", flush=True)
            ask_px = state.order_books.best_ask(self._stock)
            bid_px = state.order_books.best_bid(self._stock)
            print(f"ba = {bid_px} {ask_px} theo - {self._stock_true_theo}")

            amt = None
            side = None
            px = None

            use_bid = bid_px is not None and bid_px > self._stock_true_theo
            use_ask = ask_px is not None and ask_px < self._stock_true_theo
            if use_bid or use_ask:
                px = ask_px if use_ask else bid_px
                side = Side.BUY if use_ask else Side.SELL
                amt = int(abs(self._stock_true_theo - px) / self._qty_inc_from_theo)
                amt = min(state.order_books.qty_at(self._stock, px), amt)
                print(f"{px} @ {side} for {amt}")

            if amt is not None and amt > self._qty_min:
                qty = min(amt, self._qty_max)
                if self._use_market:
                    self.submit_to_exchange(
                        state, func=market, qty=qty, side=side, symbol=self._stock
                    )
                else:
                    self.submit_to_exchange(
                        state, func=limit, px=px, qty=qty, side=side, symbol=self._stock
                    )

            self._next_submit = ts + np.random.exponential(self._period)
