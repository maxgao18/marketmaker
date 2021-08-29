import zmq

from management.portfolio import Portfolio
from management.trade_history import TradeHistory
from management.order_book import OrderBooks
from utils.exchange import Exchange
from utils.state import State
from parsers.exchange_messages import split_topic, parse_book_str, parse_event_str


class TradeLoop:
    def __init__(
        self,
        trader,
        exchange_addr="tcp://localhost:10000",
        psub_addr="tcp://localhost:10001",
    ):
        self.exchange_addr = exchange_addr
        self.psub_addr = psub_addr
        self.trader = trader

    def run(self):
        callback_options = self.trader.callback_options()

        exchange = Exchange(self.exchange_addr)
        portfolio = Portfolio(self.trader.user)
        trade_history = TradeHistory()
        order_book = OrderBooks()

        state = State(
            portfolio=portfolio,
            exchange=exchange,
            order_books=order_book,
            trade_history=trade_history,
        )

        symbols = self.trader.symbols()

        pcontext = zmq.Context()
        psocket = pcontext.socket(zmq.SUB)
        psocket.connect(self.psub_addr)
        psocket.subscribe("")

        self.trader.init(state)
        while True:
            saw_exchange_message = True
            while True:
                try:
                    message = psocket.recv(zmq.NOBLOCK)
                    # print(message, flush=True)

                    topic, body = message.split(b" ", 1)
                    msg_type, symbol = split_topic(topic)
                    if symbol not in symbols:
                        continue

                    if msg_type == "book":
                        books = parse_book_str(body)
                        order_book.process_exchange_book(symbol, books)
                    elif msg_type == "event":
                        events = parse_event_str(body)
                        portfolio.process_exchange_events(events)
                        trade_history.process_exchange_events(events)
                    else:
                        continue

                    saw_exchange_message = True
                except zmq.ZMQError:
                    break
            if callback_options.always_run or (
                saw_exchange_message and callback_options.on_event
            ):
                self.trader.trade_loop(state)
