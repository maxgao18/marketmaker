def mid_px(book):
    ba = best_ask(book)
    bb = best_bid(book)
    if ba is None:
        return bb
    elif bb is None:
        return ba
    return (ba + bb) / 2


def best_bid(book):
    bids = sorted(book["bids"].keys(), reverse=True)
    return None if len(bids) == 0 else bids[0]


def best_ask(book):
    asks = sorted(book["asks"].keys())
    return None if len(asks) == 0 else asks[0]


class OrderBooks:
    def __init__(self):
        self._books = {}

    def process_exchange_book(self, symbol, book):
        self._books[symbol] = book
