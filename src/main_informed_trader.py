from agents.informed_trader import InformedTrader
from utils.trade_loop import TradeLoop
from run_trader import run_trader


STOCK = "BABA"
PLOT_PNL = True

trader = InformedTrader(
    user="inf-1",
    arrival_rate=3,
    stock=STOCK,
    stock_true_theo=1,
    qty_min=1,
    qty_max=20,
    qty_inc_from_theo=0.01,
    use_market=False,
)
loop = TradeLoop(trader=trader)

run_trader(loop, plot_pnl=PLOT_PNL)
