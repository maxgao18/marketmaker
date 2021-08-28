import time
import random

import numpy as np

from agents.trader import Trader
from utils.trade import cancel_all, cancel, market, limit, Side


class MarketMaker(Trader):
    def __init__(self, max_position, half_spread=0.05, stock, **kwargs):
        super().__init__(kwargs)
        self._max_position = max_position
        self._half_spread = half_spread
        self._stock = stock

    def callback_options(self):
        return Trader.CallBackOptions(always_run=True)

    def symbols(self):
        return set([self._stock])

    def init(self, state):
        self.submit_to_exchange(state, func=cancel_all, symbol="*")

    def run(self, state):
        pass
