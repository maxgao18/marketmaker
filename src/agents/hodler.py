import time
import random

import numpy as np

from agents.trader import Trader
from utils.exchange_messages import cancel_all, cancel, market, limit, Side


class HODLer(Trader):
    def __init__(
        self,
        arrival_rate,
        stock,
        px_threshold=None,
        qty_mean=5,
        qty_stddev=3,
        qty_max=999999,
        qty_min=1,
        capital_per_trade=None,
        side=Side.BUY,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._arrival_rate = arrival_rate
        self._stock = stock
        self._px_threshold = px_threshold
        self._qty_mean = qty_mean
        self._qty_max = qty_max
        self._qty_min = qty_min
        self._qty_stddev = qty_stddev
        self._capital_per_trade = capital_per_trade

        self._side = side

        self._period = 1 / arrival_rate
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
            print(f"================================{self.user}")
            print(f"holdings - {state.portfolio.holdings()}")
            print(f"bv - {self.book_value:.2f}")
            print(
                f"pnl - net ({self.realized_pnl+self.unrealized_pnl:.2f}) real ({self.realized_pnl:.2f})",
                flush=True,
            )
            mid_px = state.order_books.mid_px(self._stock)
            if (
                self._px_threshold is None
                or (self._side == Side.BUY and mid_px < self._px_threshold)
                or (self._side == Side.SELL and mid_px > self._px_threshold)
            ):

                if self._capital_per_trade is not None and mid_px is not None:
                    amt = int(self._capital_per_trade / mid_px)
                else:
                    amt = int(
                        np.random.normal(loc=self._qty_mean, scale=self._qty_stddev)
                    )

                qty = max(
                    self._qty_min,
                    min(self._qty_max, amt),
                )

                self.submit_to_exchange(
                    state, func=market, qty=qty, side=self._side, symbol=self._stock
                )

                self._next_submit = ts + np.random.exponential(self._period)
