from abc import ABC


class Signal(ABC):
    def process_exchange_events(self, symbol, events):
        pass

    def process_exchange_books(self, symbol, books):
        pass
