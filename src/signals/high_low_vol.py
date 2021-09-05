import math
import numpy as np

import utils.constants as constants
from signals.signal import Signal


class HighLowVolatility(Signal):
    _K_COEFF = np.sqrt(8 / math.pi)
    """
    High low volatility estimator for price following geometric brownian motion.

    E(1/T * sum_{t=1..T}(log H_t/L_t)) = k * sigma

    where k = sqrt(8/pi)
    """

    def __init__(self, weighted_bars):
        self._bars = weighted_bars

    def annual_volatility(self, symbol):
        bars = self._bars.bars(symbol)
        if bars is None or len(bars) == 0:
            return None

        return self._volatility(bars, constants.SECONDS_PER_TRADING_YEAR)

    def bar_volatility(self, symbol):
        bars = self._bars.bars(symbol)
        if bars is None or len(bars) == 0:
            return None

        return self._volatility(bars)

    def _volatility(self, bars, seconds_per_period=None):
        if seconds_per_period is not None:
            start_ts = bars[0].start_ts
            end_ts = bars[-1].end_ts
            scale = np.sqrt((end_ts - start_ts) * len(bars) / seconds_per_period)
        else:
            scale = len(bars)

        if scale == 0:
            return None
        high_prices = np.array([bar.high for bar in bars])
        low_prices = np.array([bar.low for bar in bars])
        log_changes = np.log(high_prices / low_prices)

        return (1 / scale) * sum(log_changes) / self._K_COEFF
