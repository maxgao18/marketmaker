import signal
import time
import threading
import sys
import os

from threading import Thread, Timer

from agents.market_maker import MarketMaker
from utils.trade_loop import TradeLoop
from utils.trade import Side
from visualizations.trader.pnl import plt_pnl

import matplotlib.pyplot as plt
import matplotlib.animation as animation


def signal_handler(signum, frame):
    sys.exit(1)


signal.signal(signal.SIGINT, signal_handler)


def run_trader(trade_loop, plot_pnl=False, plot_update_refresh_ms=1000):
    if plot_pnl:
        fig = plt.figure()
        ax1 = fig.add_subplot(1, 1, 1)

        th = threading.Thread(target=lambda: trade_loop.run())
        th.setDaemon(True)
        th.start()

        ani = animation.FuncAnimation(
            fig,
            plt_pnl(trade_loop.trader, ax1, max_lookback_sec=-1),
            interval=plot_update_refresh_ms,
        )
        plt.show()

        while True:
            time.sleep(100)
    else:
        trade_loop.run()
