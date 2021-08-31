import json

from enum import Enum


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


def book_topic(stock):
    return f"book::{stock}"


def event_topic(stock):
    return f"event::{stock}"


def split_topic(topic):
    if isinstance(topic, bytes):
        topic = topic.decode("utf-8")
    return topic.split("::", 1)


def parse_book_str(book_str):
    book = json.loads(book_str)
    for k, v in book.items():
        book[k] = {float(px): qtys for px, qtys in v.items()}
    return book


def parse_event_str(event_str):
    return json.loads(event_str)


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
