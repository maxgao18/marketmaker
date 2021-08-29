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


STOCK = "BABA"
PLT = True
CHART_UPDATE_MS = 1000


def signal_handler(signum, frame):
    sys.exit(1)


signal.signal(signal.SIGINT, signal_handler)

trader = MarketMaker(
    user="mm-3", max_position=50, half_spread=0.02, stock=STOCK, skew_quotes=True
)
loop = TradeLoop(trader=trader)

if PLT:
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)

    th = threading.Thread(target=lambda: loop.run())
    th.setDaemon(True)
    th.start()

    ani = animation.FuncAnimation(
        fig, plt_pnl(trader, ax1, max_lookback_sec=-1), interval=CHART_UPDATE_MS
    )
    plt.show()
else:
    loop.run()

while True:
    time.sleep(100)
