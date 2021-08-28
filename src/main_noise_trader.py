import zmq
import json
import random
import time
import signal

from agents.noise_trader import NoiseTrader
from utils.trade_loop import TradeLoop
from utils.trade import Side


STOCK = "BABA"


def signal_handler(signum, frame):
    exit(1)


signal.signal(signal.SIGINT, signal_handler)

trader = NoiseTrader(user="nt-1", arrival_rate=1, stock=STOCK, sides=[Side.BUY])
loop = TradeLoop(trader=trader)

loop.run()
