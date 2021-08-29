import signal

from agents.market_maker import MarketMaker
from utils.trade_loop import TradeLoop
from utils.trade import Side


STOCK = "BABA"


def signal_handler(signum, frame):
    exit(1)


signal.signal(signal.SIGINT, signal_handler)

trader = MarketMaker(user="mm-1", max_position=50, half_spread=0.03, stock=STOCK)
loop = TradeLoop(trader=trader)

loop.run()
