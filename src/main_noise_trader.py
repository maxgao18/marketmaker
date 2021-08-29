import signal

from agents.noise_trader import NoiseTrader
from utils.trade_loop import TradeLoop
from utils.trade import Side


STOCK = "BABA"


def signal_handler(signum, frame):
    exit(1)


signal.signal(signal.SIGINT, signal_handler)

trader = NoiseTrader(user="lim-odr", arrival_rate=3, stock=STOCK, use_market=False)
loop = TradeLoop(trader=trader)

loop.run()
