import heapq
import time

from collections import defaultdict


_CASH = "$"

_IN_FLIGHT_SEC_THRESHOLD = 2


class Portfolio:
    def __init__(self, user, initial_capital=0):
        self._user = user
        self._initial_capital = initial_capital

        self._holdings = defaultdict(lambda: 0)
        self._holdings[_CASH] = initial_capital
        self._outstanding_orders_by_symbol = defaultdict(dict)
        self._book_value = defaultdict(lambda: 0)
        self._in_flight_orders_by_symbol = defaultdict(dict)
        self._in_flight_send_time = []

    def process_exchange_events(self, events):
        self._clear_old_inflight()

        for e in events["executed"]:
            self._in_flight_orders_by_symbol[e["symbol"]].pop(e["id"], None)
            if e["user"] != self._user:
                continue

            event_type = e["type"]
            if event_type == "TRADE":
                self._process_trade_event(e)
            elif event_type == "ADD":
                self._process_add_event(e)
            elif event_type == "CANCEL":
                self._process_cancel_event(e)
        for e in events["failed"]:
            symbol = e.get("symbol")
            if symbol in self._in_flight_orders_by_symbol:
                self._in_flight_orders_by_symbol[symbol].pop(e.get("id"), None)

    def process_new_order(self, order):
        self._clear_old_inflight()

        symbol = order["symbol"]
        if symbol == "*":
            return

        oid = order["id"]
        self._in_flight_orders_by_symbol[symbol][oid] = order
        heapq.heappush(self._in_flight_send_time, (time.time(), symbol, oid))

    def holdings(self):
        return self._holdings

    def book_values(self):
        return self._book_value

    def holding(self, symbol):
        return self._holdings.get(symbol, 0)

    def book_value(self, symbol):
        return self._book_value.get(symbol, 0)

    def cash(self):
        return self._holdings[_CASH]

    def outstanding_orders(self, symbol):
        return self._outstanding_orders_by_symbol[symbol]

    def in_flight_orders(self, symbol):
        self._clear_old_inflight()
        return self._in_flight_orders_by_symbol[symbol]

    def _process_trade_event(self, event):
        symbol = event["symbol"]
        direction = event["side"]
        sgn = 1 if direction == "BUY" else -1
        qty = event["qty"]
        px = event["px"]
        book_qty = sgn * qty

        prev_holdings = self._holdings[symbol]
        self._holdings[symbol] += book_qty
        if prev_holdings * book_qty >= 0:
            self._book_value[symbol] += book_qty * px
        elif abs(prev_holdings) >= qty:
            self._book_value[symbol] *= 1 - qty / abs(prev_holdings)
        else:
            self._book_value[symbol] = self._holdings[symbol] * px

        self._holdings[_CASH] -= book_qty * px
        if self._holdings[symbol] == 0 and symbol != _CASH:
            self._holdings.pop(symbol, None)

        order_id = event["id"]
        status = event["status"]
        if order_id in self._outstanding_orders_by_symbol[symbol]:
            if status == "FILLED":
                self._outstanding_orders_by_symbol[symbol].pop(order_id, None)
            elif status == "PARTIAL":
                self._outstanding_orders_by_symbol[symbol][order_id]["qty"] -= event[
                    "qty"
                ]

    def _process_add_event(self, event):
        symbol = event["symbol"]
        order_id = event["id"]
        self._outstanding_orders_by_symbol[symbol][order_id] = event

    def _process_cancel_event(self, event):
        symbol = event["symbol"]
        cancel_id = event["order_id"]
        self._outstanding_orders_by_symbol[symbol].pop(cancel_id, None)

    def _clear_old_inflight(self):
        ts = time.time()
        while (
            len(self._in_flight_send_time) > 0
            and ts - self._in_flight_send_time[0][0] > _IN_FLIGHT_SEC_THRESHOLD
        ):
            t, symbol, id = heapq.heappop(self._in_flight_send_time)
            self._in_flight_orders_by_symbol[symbol].pop(id, None)
