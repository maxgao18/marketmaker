from exchange.order_book import OrderBook
from exchange.order_types import Cancel, CancelAll, Limit, Market, Side


class StockExchange:
    def __init__(self, symbols):
        self._books = {sym: OrderBook() for sym in symbols}

    def book(self, symbol):
        return self._books.get(symbol)

    def _remap_output(self, symbol, o):
        x, y = o
        for m in x:
            m["symbol"] = symbol
        for m in y:
            m["symbol"] = symbol
        return x, y

    def submit(self, order):
        if order.symbol != "*" and order.symbol not in self._books:
            return [], [
                {
                    "user": order.user,
                    "id": order.id,
                    "symbol": order.symbol,
                    "type": "?",
                    "status": "FAILED",
                }
            ]

        if order.symbol == "*":
            s = []
            e = []
            for symbol, book in self._books.items():
                try:
                    s1, e1 = self._remap_output(symbol, book.execute_order(order))
                    s += s1
                    e += e1
                except:
                    pass
            return s, e

        return self._remap_output(
            order.symbol, self._books[order.symbol].execute_order(order)
        )


if __name__ == "__main__":
    ex = StockExchange(["BABA"])
    print(
        ex.submit(Limit(user="u1", px=1.00, qty=2, side=Side.BUY, id=1, symbol="BABA"))
    )
    print(
        ex.submit(Limit(user="u2", px=1.01, qty=1, side=Side.SELL, id=1, symbol="BABA"))
    )
    print(
        ex.submit(Limit(user="u3", px=1.02, qty=3, side=Side.SELL, id=1, symbol="BABA"))
    )
    print(
        ex.submit(Limit(user="u4", px=1.02, qty=2, side=Side.BUY, id=1, symbol="BABA"))
    )
    print(ex.submit(CancelAll(user="u3", id=2, symbol="*")))
    # print(ex.submit("user-1", Cancel(order_id=1, id=2, symbol="BABA")))
    # print(ex.submit("user-2", Market(qty=2, side=Side.SELL, id=2, symbol="BABA")))
