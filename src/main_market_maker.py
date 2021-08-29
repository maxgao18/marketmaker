import signal
import time
import threading
import sys

from agents.market_maker import MarketMaker
from utils.trade_loop import TradeLoop
from utils.trade import Side

import matplotlib.pyplot as plt
import matplotlib.animation as animation


STOCK = "BABA"
PLT = True
CHART_UPDATE_MS = 1000


def signal_handler(signum, frame):
    sys.exit(1)


def plt_pnl(mm, ax):
    pnls = []
    ts = []
    def update_plot(i):
      pnls.append(mm._bv)
      ts.append(int(time.time()))

      ax.clear()
      ax.set_ylabel("pnl")
      ax.set_xlabel("timestamp")
      ax.plot(ts, pnls)

    return update_plot


signal.signal(signal.SIGINT, signal_handler)

trader = MarketMaker(user="mm-1", max_position=50, half_spread=0.03, stock=STOCK)
loop = TradeLoop(trader=trader)

if PLT:
  fig = plt.figure()
  ax1 = fig.add_subplot(1, 1, 1)

  th = threading.Thread(
      target=lambda: loop.run()
  )
  th.start()

  ani = animation.FuncAnimation(
      fig, plt_pnl(trader, ax1), interval=CHART_UPDATE_MS
  )
  plt.show()
else:
  loop.run()

