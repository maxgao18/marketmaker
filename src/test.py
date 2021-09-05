import numpy as np

from signals.weighted_bars import Bar
from signals.drift import Drift
from signals.high_low_vol import HighLowVolatility

import matplotlib.pyplot as plt


def check_drift_and_volatility():
    intervals = 500
    vol = 0.5
    dri = 0 - 0.5 * vol ** 2

    drift = dri * np.arange(0, intervals)
    noise = np.random.normal(loc=0, scale=vol, size=intervals).cumsum()
    # print(noise)
    returns = np.exp(drift + noise)
    # plt.plot(noise)
    # plt.show()

    bars = []
    for t in range(int(intervals / 4)):
        pxs = returns[t : t + 4]
        bars.append(
            Bar(
                volume=1,
                high=max(pxs),
                low=min(pxs),
                open=pxs[0],
                close=pxs[-1],
                start_ts=4 * t,
                end_ts=4 * t + 3,
            )
        )
    dr = Drift(None)
    hl = HighLowVolatility(None)
    # print(bars)
    print(f"Actual drift = {dri}, Estimated drift = {dr._drift(bars, 1)}")
    print(f"Actual vol = {vol}, Estimated vol = {hl._volatility(bars, 1)}")


if __name__ == "__main__":
    check_drift_and_volatility()
