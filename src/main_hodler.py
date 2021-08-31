from agents.hodler import HODLer
from utils.trade_loop import TradeLoop
from utils.exchange_messages import Side
from run_trader import run_trader


STOCK = "BABA"

trader = HODLer(
    user="hodl",
    arrival_rate=3,
    stock=STOCK,
    qty_mean=10,
    qty_stddev=5,
    capital_per_trade=10,
)
loop = TradeLoop(trader=trader)

run_trader(loop)
