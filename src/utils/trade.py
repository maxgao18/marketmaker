from enum import Enum


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


def market(user, id, symbol, qty, side):
    return {"user": user, "id": id, "symbol": symbol, "qty": qty, "side": side}


def cancel(user, id, order_id, symbol):
    return {
        "user": user,
        "id": id,
        "order_id": order_id,
        "symbol": symbol,
        "type": "CANCEL",
    }


def limit(user, id, symbol, px, qty, side):
    return {
        "user": user,
        "id": id,
        "symbol": symbol,
        "side": side,
        "qty": qty,
        "px": px,
        "type": "LIMIT",
    }


def cancel_all(user, id, symbol="*"):
    return {
        "user": user,
        "id": id,
        "symbol": symbol,
        "type": "CANCELALL",
    }