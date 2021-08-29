from collections import defaultdict, namedtuple

import heapq

from exchange.order_types import Cancel, CancelAll, Market, Limit, Side


class UnknownOrderException(Exception):
    pass


class DuplicateIdException(Exception):
    pass


BookEntry = namedtuple("BookEntry", ["sort", "ts", "uid", "id", "user", "px", "qty"])


class OrderBook:
    def __init__(self):
        self.tick = 0
        self.buy_side = []
        self.sell_side = []
        self.uids = set()

    def execute_order(self, order):
        if order.uid in self.uids:
            raise DuplicateIdException(f"Duplicate id {order.id} in {order}")

        self.tick += 1

        if isinstance(order, Cancel):
            return self._exec_cancel(order)
        elif isinstance(order, CancelAll):
            return self._exec_cancel_all(order)
        elif isinstance(order, Market) or isinstance(order, Limit):
            return self._exec_stock_order(order)

        raise UnknownOrderException(f"Unknown order {order}")

    def dump(self, max_levels=-1):
        bids = defaultdict(list)
        asks = defaultdict(list)

        for b in self.buy_side:
            bids[b.px].append(b.qty)
        for a in self.sell_side:
            asks[a.px].append(a.qty)

        if max_levels > 0:
            highest_bids = list(sorted(bids.keys()))[-max_levels:]
            lowest_asks = list(sorted(asks.keys()))[:max_levels]
            nb = {}
            na = {}
            for b in highest_bids:
                nb[b] = bids[b]
            for a in lowest_asks:
                na[a] = asks[a]
            bids, asks = nb, na
        return {"bids": bids, "asks": asks}

    def _exec_cancel(self, order):
        if order.uorder_id not in self.uids:
            return [], [
                {
                    "id": order.id,
                    "user": order.user,
                    "order_id": order.order_id,
                    "type": "CANCEL",
                    "status": "FAILED",
                }
            ]

        self.uids.remove(order.uorder_id)
        canceled_order = None
        side = None
        for o in self.buy_side:
            if o.uid == order.uorder_id:
                canceled_order = o
                side = "BUY"
                self.buy_side = [o for o in self.buy_side if o.uid != order.uorder_id]
                heapq.heapify(self.buy_side)
        if canceled_order is None:
            for o in self.sell_side:
                if o.uid == order.uorder_id:
                    canceled_order = o
                    side = "SELL"
                    self.sell_side = [
                        o for o in self.sell_side if o.uid != order.uorder_id
                    ]
                    heapq.heapify(self.sell_side)
        return [
            {
                "id": order.id,
                "user": order.user,
                "order_id": order.order_id,
                "type": "CANCEL",
                "status": "FILLED",
                "qty": canceled_order.qty,
                "px": canceled_order.px,
                "side": side,
            }
        ], []

    def _exec_cancel_all(self, order):
        user = order.user
        canceled = []
        for book, side in [(self.buy_side, "BUY"), (self.sell_side, "SELL")]:
            for o in book:
                if o.user == user:
                    canceled.append(
                        {
                            "id": order.id,
                            "user": user,
                            "order_id": o.id,
                            "type": "CANCEL",
                            "status": "FILLED",
                            "qty": o.qty,
                            "px": o.px,
                            "side": side,
                        }
                    )
                    self.uids.remove(o.uid)
        self.buy_side = [o for o in self.buy_side if o.user != user]
        self.sell_side = [o for o in self.sell_side if o.user != user]
        heapq.heapify(self.buy_side)
        heapq.heapify(self.sell_side)

        return canceled, []

    def _exec_stock_order(self, order):
        if isinstance(order, Market):
            order_px = 1 << 30
            if order.side == Side.SELL:
                order_px *= -1
        else:
            order_px = order.px
        if order.side == Side.BUY:
            order_book = self.buy_side
            match_book = self.sell_side
            order_cmp_value = order_px
            order_sort_value = -order_px
            order_side = "BUY"
            match_side = "SELL"
        else:
            order_book = self.sell_side
            match_book = self.buy_side
            order_cmp_value = -order_px
            order_sort_value = order_px
            order_side = "SELL"
            match_side = "BUY"

        initial_qty = order.qty
        executions = []
        failed = []
        total_px = 0
        while (
            order.qty > 0
            and len(match_book) > 0
            and order_cmp_value >= match_book[0].sort
        ):
            top_order = heapq.heappop(match_book)
            qty = min(top_order.qty, order.qty)
            order.qty -= qty
            total_px += top_order.px * qty
            new_top_order = BookEntry(
                top_order.sort,
                top_order.ts,
                top_order.uid,
                top_order.id,
                top_order.user,
                top_order.px,
                top_order.qty - qty,
            )
            executions.append(
                {
                    "id": top_order.id,
                    "user": top_order.user,
                    "px": top_order.px,
                    "qty": qty,
                    "side": match_side,
                    "type": "TRADE",
                    "status": "FILLED" if new_top_order.qty == 0 else "PARTIAL",
                }
            )
            if new_top_order.qty > 0:
                heapq.heappush(match_book, new_top_order)
            else:
                self.uids.remove(top_order.uid)

        qty = initial_qty - order.qty
        if qty > 0:
            executions.append(
                {
                    "id": order.id,
                    "user": order.user,
                    "px": total_px / qty,
                    "qty": qty,
                    "side": order_side,
                    "type": "TRADE",
                    "status": "FILLED" if order.qty == 0 else "PARTIAL",
                }
            )

        if order.qty > 0:
            if isinstance(order, Limit):
                heapq.heappush(
                    order_book,
                    BookEntry(
                        order_sort_value,
                        self.tick,
                        order.uid,
                        order.id,
                        order.user,
                        order.px,
                        order.qty,
                    ),
                )
                self.uids.add(order.uid)
                executions.append(
                    {
                        "id": order.id,
                        "user": order.user,
                        "px": order.px,
                        "qty": order.qty,
                        "side": order_side,
                        "type": "ADD",
                        "status": "FILLED",
                    }
                )
            else:
                failed.append(
                    {
                        "id": order.id,
                        "user": order.user,
                        "qty": order.qty,
                        "side": order_side,
                        "type": "TRADE",
                        "status": "FAILED",
                    }
                )
        return executions, failed
