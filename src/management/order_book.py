def _mid_px(book):
    ba = _best_ask(book)
    bb = _best_bid(book)
    if ba is None:
        return bb
    elif bb is None:
        return ba
    return (ba + bb) / 2


def _best_bid(book):
    if book is None:
        return None

    bids = sorted(book["bids"].keys(), reverse=True)
    return None if len(bids) == 0 else bids[0]


def _best_ask(book):
    if book is None:
        return None

    asks = sorted(book["asks"].keys())
    return None if len(asks) == 0 else asks[0]


class OrderBooks:
    def __init__(self):
        self._books = {}

    def process_exchange_book(self, symbol, book):
        self._books[symbol] = book

    def mid_px(self, symbol):
        return _mid_px(self._books.get(symbol))

    def best_bid(self, symbol):
        return _best_bid(self._books.get(symbol))

    def best_ask(self, symbol):
        return _best_ask(self._books.get(symbol))

    def book(self, symbol):
        return self._books.get(symbol)
