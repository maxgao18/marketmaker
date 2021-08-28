class State:
    def __init__(self, portfolio, exchange, order_books, trade_history):
        self.portfolio = portfolio
        self.exchange = exchange
        self.order_books = order_books
        self.trade_history = trade_history
