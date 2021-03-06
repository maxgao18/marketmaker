from abc import ABC, abstractmethod


class Trader(ABC):
    class CallBackOptions:
        def __init__(self, always_run=False, on_event=True):
            self.always_run = always_run
            self.on_event = on_event

    def __init__(self, user):
        self.user = user
        self.msg_id = 0

        self.book_value = 0
        self.realized_pnl = 0
        self.unrealized_pnl = 0
        self.signals = []

    def callback_options(self):
        return Trader.CallBackOptions()

    @abstractmethod
    def symbols(self):
        pass

    @abstractmethod
    def init(self, state):
        pass

    @abstractmethod
    def run(self, state):
        pass

    def trade_loop(self, state):
        self.set_pnls(state)
        self.run(state)

    def submit_to_exchange(self, state, msg=None, func=None, **kwargs):
        self.msg_id += 1
        if msg is not None:
            msg["user"] = self.user
            msg["id"] = str(self.msg_id)
        elif func is not None:
            msg = func(user=self.user, id=self.msg_id, **kwargs)
        else:
            return

        state.portfolio.process_new_order(msg)
        state.exchange.submit(msg)

    def set_pnls(self, state):
        self.book_value = sum(state.portfolio.book_values().values())
        self.realized_pnl = self.book_value - state.portfolio.initial_capital

        unrealized_pnl = 0
        for stock, qty in state.portfolio.holdings().items():
            mid_px = state.order_books.mid_px(stock)
            if mid_px is not None:
                unrealized_pnl += qty * mid_px - state.portfolio.book_value(stock)
        self.unrealized_pnl = unrealized_pnl

    def add_signal(self, signal):
        if isinstance(signal, list):
            self.signals += signal
        else:
            self.signals.append(signal)
