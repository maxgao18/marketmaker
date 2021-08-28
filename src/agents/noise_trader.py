import time
import random

import numpy as np

from agents.trader import Trader
from utils.trade import cancel_all, cancel, market, limit, Side


class NoiseTrader(Trader):
    def __init__(self, arrival_rate, stock, sides=None, **kwargs):
        super().__init__(kwargs)
        self._arrival_rate = arrival_rate
        self._stock = stock
        self._sides = sides or [Side.BUY, Side.SELL]

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
            print("================================")
            print(f"holding - {state.portfolio.holdings()}")
            print(f"bv - {state.portfolio.book_values()}")
            print(f"pv - {sum(state.portfolio.book_values().values())}")
            px = random.randint(50, 100) / 100
            qty = random.randint(1, 10)
            side = random.choice(self._sides)

            self.submit_to_exchange(
                state, func=limit, px=px, qty=qty, side=side, symbol=self._stock
            )

            self._next_submit = ts + np.random.exponential(self._period)
