import math
import numpy as np

import utils.constants as constants
from signals.signal import Signal


class Drift(Signal):
    """
    Drift estimator.

    drift = E(log(c_i/o_i)), c_i and o_i the close/open prices
    """

    def __init__(self, weighted_bars):
        self._bars = weighted_bars

    def annual_drift(self, symbol):
        bars = self._bars.bars(symbol)
        if bars is None or len(bars) == 0:
            return None

        return self._drift(bars, constants.SECONDS_PER_TRADING_YEAR)

    def bar_drift(self, symbol):
        bars = self._bars.bars(symbol)
        if bars is None or len(bars) == 0:
            return None

        return self._drift(bars)

    def _drift(self, bars, seconds_per_period=None):
        if seconds_per_period is not None:
            start_ts = bars[0].start_ts
            end_ts = bars[-1].end_ts
            time_per_bar = (end_ts - start_ts) / len(bars)
            # I dont think this is right because AM != GM?
            scale = time_per_bar / seconds_per_period
        else:
            scale = len(bars)

        if scale == 0:
            return None
        open_prices = np.array([bar.open for bar in bars])
        close_prices = np.array([bar.close for bar in bars])
        log_changes = np.log(close_prices / open_prices)

        return (1 / scale) * sum(log_changes)
