from enum import Enum


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


def market(user, id, symbol, qty, side):
    return {
        "user": user,
        "id": str(id),
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": "MARKET",
    }


def cancel(user, id, order_id, symbol):
    return {
        "user": user,
        "id": str(id),
        "order_id": order_id,
        "symbol": symbol,
        "type": "CANCEL",
    }


def limit(user, id, symbol, px, qty, side):
    return {
        "user": user,
        "id": str(id),
        "symbol": symbol,
        "side": side,
        "qty": qty,
        "px": px,
        "type": "LIMIT",
    }


def cancel_all(user, id, order_ids="*", symbol="*"):
    return {
        "user": user,
        "id": str(id),
        "symbol": symbol,
        "order_ids": order_ids,
        "type": "CANCELALL",
    }
