import json


def book_topic(stock):
    return f"book::{stock}"


def event_topic(stock):
    return f"event::{stock}"


def split_topic(topic):
    if isinstance(topic, bytes):
        topic = str(topic)
    return topic.split("::", 1)


def parse_book_str(book_str):
    book = json.loads(book_str)
    for k, v in book.items():
        book[k] = {float(px): int(qty) for px, qty in v.items()}
    return book


def parse_event_str(event_str):
    return json.loads(event_str)
