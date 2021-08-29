from collections import defaultdict
import json
import time
import zmq
import signal
import traceback

import numpy as np

from exchange.stock_exchange import StockExchange
from exchange.order_types import Cancel, CancelAll, Limit, Market, Side


STOCK = "BABA"
BOOK_LEVELS = 8
_EVENT_TOPIC_FORMAT = "event::{}"
_BOOK_TOPIC_FORMAT = "book::{}"

interrupted = False


def signal_handler(signum, frame):
    global interrupted
    interrupted = True


def parse_side(side):
    if side == "BUY":
        return Side.BUY
    elif side == "SELL":
        return Side.SELL


def parse_message(msg):
    try:
        user = msg["user"]
        order_type = msg["type"]
        o_id = msg["id"]
        symbol = msg["symbol"]
        if order_type == "CANCEL":
            return Cancel(user=user, order_id=msg["order_id"], id=o_id, symbol=symbol)
        elif order_type == "CANCELALL":
            return CancelAll(user=user, id=o_id, symbol=symbol)
        elif order_type == "MARKET":
            side = parse_side(msg["side"])
            if side is not None:
                return Market(
                    user=user, qty=int(msg["qty"]), side=side, id=o_id, symbol=symbol
                )
        elif order_type == "LIMIT":
            side = parse_side(msg["side"])
            px = float(msg["px"])
            if np.round(px, decimals=2) == px and side is not None:
                return Limit(
                    user=user,
                    qty=int(msg["qty"]),
                    px=float(msg["px"]),
                    side=side,
                    id=o_id,
                    symbol=symbol,
                )
    except:
        pass

    return None


def run_exchange(symbol, server_sock, pub_sock):
    signal.signal(signal.SIGINT, signal_handler)
    ex = StockExchange([symbol])

    # listening
    scontext = zmq.Context()
    ssocket = scontext.socket(zmq.REP)
    ssocket.bind(server_sock)

    # pub
    pcontext = zmq.Context()
    psocket = pcontext.socket(zmq.PUB)
    psocket.bind(pub_sock)

    while not interrupted:
        #  Wait for next request from client
        try:
            message = ssocket.recv(zmq.NOBLOCK)
            ssocket.send_string("ACK")
        except zmq.ZMQError:
            continue

        try:
            loaded = json.loads(message)
            order = parse_message(loaded)
            if order is None:
                events = {
                    "executed": [],
                    "failed": [loaded],
                }
                sym = loaded.get("symbol", "?")
                psocket.send_string(
                    f"{_EVENT_TOPIC_FORMAT.format(sym)} {json.dumps(events)}"
                )

            s, f = ex.submit(order)
            if order.symbol == "*":
                s_symbol = defaultdict(list)
                f_symbol = defaultdict(list)
                symbols = set()

                for e in s:
                    s_symbol[e["symbol"]].append(e)
                    symbols.add(e["symbol"])
                for e in f:
                    f_symbol[e["symbol"]].append(e)
                    symbols.add(e["symbol"])

                for sym in symbols:
                    events = {
                        "executed": s_symbol[sym],
                        "failed": f_symbol[sym],
                    }

                    psocket.send_string(
                        f"{_EVENT_TOPIC_FORMAT.format(sym)} {json.dumps(events)}"
                    )

                    book = ex.book(sym)
                    psocket.send_string(
                        f"{_BOOK_TOPIC_FORMAT.format(sym)} {json.dumps(book.dump(max_levels=BOOK_LEVELS))}"
                    )
            else:
                events = {
                    "executed": s,
                    "failed": f,
                }

                psocket.send_string(
                    f"{_EVENT_TOPIC_FORMAT.format(order.symbol)} {json.dumps(events)}"
                )

                book = ex.book(order.symbol)
                psocket.send_string(
                    f"{_BOOK_TOPIC_FORMAT.format(order.symbol)} {json.dumps(book.dump(max_levels=BOOK_LEVELS))}"
                )
        except Exception as e:
            traceback.print_exc()


if __name__ == "__main__":
    run_exchange(STOCK, "tcp://*:10000", "tcp://*:10001")
