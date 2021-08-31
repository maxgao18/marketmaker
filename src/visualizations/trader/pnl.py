import time

from collections import deque


def plt_pnl(trader, ax, max_lookback_sec=-1):
    realized_pnls = deque()
    net_pnls = deque()
    tss = deque()

    def update_plot(i):
        realized_pnls.append(trader.realized_pnl)
        net_pnls.append(trader.realized_pnl + trader.unrealized_pnl)
        ts = int(time.time())
        tss.append(ts)
        while max_lookback_sec > 0 and len(tss) > 0 and ts - max_lookback_sec > tss[0]:
            tss.popleft()
            realized_pnls.popleft()

        ax.clear()
        ax.set_title(f"{trader.user} P/L")
        ax.set_ylabel("P/L")
        ax.set_xlabel("Timestamp")
        ax.plot(tss, realized_pnls, label="Realized P/L")
        ax.plot(tss, net_pnls, label="Total P/L")
        ax.legend()

    return update_plot
