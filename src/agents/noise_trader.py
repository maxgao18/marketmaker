import time
import random

import numpy as np

from agents.trader import Trader
from utils.trade import cancel_all, cancel, market, limit, Side


class NoiseTrader(Trader):
    def __init__(
        self,
        arrival_rate,
        stock,
        px_stddev=0.05,
        qty_mean=5,
        qty_stddev=3,
        qty_max=999999,
        qty_min=1,
        sides=None,
        use_market=False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._arrival_rate = arrival_rate
        self._stock = stock
        self._px_stddev = px_stddev
        self._qty_mean = qty_mean
        self._qty_max = qty_max
        self._qty_min = qty_min
        self._qty_stddev = qty_stddev

        self._sides = sides or [Side.BUY, Side.SELL]

        self._period = 1 / arrival_rate
        self._use_market = use_market
        self._next_submit = 0
        self._cancel_old_orders_beyond_sec = 60

    def callback_options(self):
        return Trader.CallBackOptions(always_run=True)

    def symbols(self):
        return set([self._stock])

    def init(self, state):
        self.submit_to_exchange(state, func=cancel_all, symbol="*")

    def run(self, state):
        ts = time.time()

        old_orders = [
            id
            for id, o in state.portfolio.outstanding_orders(self._stock).items()
            if ts - o["recv_time"] > self._cancel_old_orders_beyond_sec
        ]
        in_flight_cancels = []
        for o in state.portfolio.in_flight_orders(self._stock).values():
            otype = o["type"]
            if otype == "CANCEL":
                in_flight_cancels.append(o["order_id"])
            elif otype == "CANCELALL" and isinstance(o["order_ids"], list):
                in_flight_cancels += o["order_ids"]

        to_cancel = set(old_orders).difference(in_flight_cancels)
        if len(to_cancel) > 0:
            self.submit_to_exchange(
                state, func=cancel_all, order_ids=list(to_cancel), symbol=self._stock
            )

        if self._next_submit < ts:
            print(f"================================{self.user}")
            print(f"holdings - {state.portfolio.holdings()}")
            print(f"bv - {self.book_value}")
            print(f"pnl - {self.realized_pnl}", flush=True)
            mid_px = state.order_books.mid_px(self._stock)
            random_px = (
                np.random.normal(loc=mid_px, scale=self._px_stddev)
                if mid_px is not None
                else np.random.normal(0.5, 0.1)
            )
            px = max(0.01, np.round(random_px, decimals=2))
            print(f"mpx {mid_px} rpx {px}")
            qty = max(
                self._qty_min,
                min(
                    self._qty_max,
                    int(np.random.normal(loc=self._qty_mean, scale=self._qty_stddev)),
                ),
            )
            side = random.choice(self._sides)

            if self._use_market:
                self.submit_to_exchange(
                    state, func=market, qty=qty, side=side, symbol=self._stock
                )
            else:
                self.submit_to_exchange(
                    state, func=limit, px=px, qty=qty, side=side, symbol=self._stock
                )

            self._next_submit = ts + np.random.exponential(self._period)
