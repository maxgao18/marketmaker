from agents.noise_trader import NoiseTrader
from utils.trade_loop import TradeLoop
from utils.trade import Side
from run_trader import run_trader


STOCK = "BABA"

trader = NoiseTrader(
    user="mkt-odr",
    arrival_rate=3,
    stock=STOCK,
    qty_mean=10,
    qty_stddev=5,
    use_market=False,
)
loop = TradeLoop(trader)

run_trader(loop)
