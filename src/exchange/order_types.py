from enum import Enum


class Side(Enum):
    BUY = 0
    SELL = 1


class Order:
    def __init__(self, id, user, symbol):
        self.id = id
        self.user = user
        self.symbol = symbol
        self.uid = f"{user}::{id}"


class Cancel(Order):
    def __init__(self, order_id, **kwargs):
        super().__init__(**kwargs)
        self.order_id = order_id
        self.uorder_id = f"{self.user}::{order_id}"


class CancelAll(Order):
    def __init__(self, order_ids, **kwargs):
        super().__init__(**kwargs)
        self.order_ids = order_ids


class Limit(Order):
    def __init__(self, px, qty, side, **kwargs):
        super().__init__(**kwargs)
        self.side = side
        self.px = px
        self.qty = qty


class Market(Order):
    def __init__(self, qty, side, **kwargs):
        super().__init__(**kwargs)
        self.side = side
        self.qty = qty
