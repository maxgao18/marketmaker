import time
import numpy as np

from collections import deque, defaultdict

from signals.signal import Signal


class VPIN(Signal):
    """
    Inefficent implementation of volume probability of informed trading.

    Ideally, uses volume bars but that is not yet implemented.
    """

    def __init__(self, trade_direction):
        self._trade_direction = trade_direction
        self._vpin = {}
        self._buy_sell_volume_diff = {}
        self._recalulate_vpin = defaultdict(lambda: True)

    def process_exchange_events(self, symbol, events):
        self._recalulate_vpin[symbol] = True

    def vpin(self, symbol):
        if symbol not in self._vpin or self._recalulate_vpin[symbol]:
            self._recalculate(symbol)
        return self._vpin[symbol]

    def buy_volume_pct(self, symbol):
        if symbol not in self._vpin or self._recalulate_vpin[symbol]:
            self._recalculate(symbol)
        return (self._buy_sell_volume_diff[symbol] + 1) / 2

    def sell_volume_pct(self, symbol):
        return 1 - self.buy_volume_pct(symbol)

    def _recalculate(self, symbol):
        volumes = np.array(self._trade_direction.volumes(symbol))
        directions = np.array(self._trade_direction.directions(symbol))
        self._buy_sell_volume_diff[symbol] = (
            0 if len(volumes) == 0 else np.dot(volumes, directions) / sum(volumes)
        )
        self._vpin[symbol] = abs(self._buy_sell_volume_diff[symbol])
        self._recalulate_vpin[symbol] = False
