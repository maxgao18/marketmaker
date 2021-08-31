from agents.market_maker import MarketMaker
from utils.trade_loop import TradeLoop
from utils.exchange_messages import Side
from run_trader import run_trader


STOCK = "BABA"
PLOT_PNL = True

trader = MarketMaker(
    user="mm-no-vpin",
    max_position=50,
    half_spread=0.01,
    vpin_multiplier=0.3,
    stock=STOCK,
    skew_quotes=False,
)
loop = TradeLoop(trader=trader)

run_trader(loop, plot_pnl=PLOT_PNL)
