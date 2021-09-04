import numpy as np

from signals.weighted_bars import Bar
from signals.high_low_vol import HighLowVolatility

import matplotlib.pyplot as plt


def check_volatility():
    intervals = 100
    vol = 0.5
    drift = (0.15 - 0.5 * vol ** 2) * np.arange(0, intervals)
    noise = np.random.normal(loc=0, scale=vol, size=intervals).cumsum()
    # print(noise)
    returns = np.exp(drift + noise)
    # plt.plot(noise)
    # plt.show()

    bars = []
    for t in range(25):
        pxs = returns[t : t + 4]
        bars.append(
            Bar(
                volume=1,
                high=max(pxs),
                low=min(pxs),
                open=pxs[0],
                close=pxs[-1],
                start_ts=t,
                end_ts=t + 3,
            )
        )
    hl = HighLowVolatility(None)
    # print(bars)
    print(f"Actual vol = {vol}, Estimated vol = {hl._volatility(1, bars)}")


if __name__ == "__main__":
    check_volatility()
