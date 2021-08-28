from asciimatics.screen import ManagedScreen
from collections import defaultdict, deque

import asciimatics.constants as asciiconsts
import numpy as np


SELL_COLOR = asciiconsts.COLOUR_RED
BUY_COLOR = asciiconsts.COLOUR_BLUE
_ASCII_X_START = 0
_ASCII_Y_START = 4


class ScreenState:
    def __init__(self, screen, symbol):
        self.screen = screen
        self.best_bids = deque()
        self.best_asks = deque()
        self.symbol = symbol

    def update(self, book, levels=21, px_inc=0.01, hist_len=15):
        px_inc_inv = 1 / px_inc
        for k, v in book.items():
            nm = {}
            nm = {
                int(float(px) * px_inc_inv) * px_inc: int(qty) for px, qty in v.items()
            }
            book[k] = nm

        bids = sorted(book["bids"].items(), reverse=True)
        asks = sorted(book["asks"].items())

        best_ask = None if len(asks) == 0 else asks[0][0]
        best_bid = None if len(bids) == 0 else bids[0][0]

        self.best_bids.append(best_bid)
        self.best_asks.append(best_ask)

        if len(self.best_bids) > hist_len:
            self.best_bids.popleft()
            self.best_asks.popleft()

        _write_book_to_screen(
            self.screen,
            self.symbol,
            book["bids"],
            book["asks"],
            levels,
            px_inc,
            hist_len,
            self.best_bids,
            self.best_asks,
        )


def _write_book_to_screen(
    screen, symbol, bids, asks, levels, px_inc, hist_len, bid_hist, ask_hist
):
    def _format_order(o):
        sz = f"{o}"
        spcs = "." * (o - len(sz))
        return f"{sz}{spcs}"

    def _format_level(px, px_decimals, orders):
        px = f"{px:.2f}"
        spcs = " " * (px_decimals - len(px) + 3)
        orderstr = (
            "".join(_format_order(o) for o in orders) if orders is not None else ""
        )
        return f"| {spcs}{px} | {orderstr}"

    inverse_px_inc = 1 / px_inc
    screen.clear()
    best_ask = ask_hist[-1]
    best_bid = bid_hist[-1]
    if best_ask is None:
        mid_px = best_bid if best_bid is not None else 0
    elif best_bid is None:
        mid_px = best_ask if best_ask is not None else 0
    else:
        mid_px = int(inverse_px_inc * (best_bid + best_ask) / 2) * px_inc
    lowest_px = mid_px - int(levels / 2) * px_inc
    highest_px = lowest_px + (levels - 1) * px_inc

    px_range = [lowest_px + i * px_inc for i in range(levels)]

    px_decimals = max(1, len(f"{int(highest_px)}"), len(f"{int(lowest_px)}"))

    if lowest_px < 0:
        px_decimals += 1

    screen.print_at(
        symbol, _ASCII_X_START, 0, asciiconsts.COLOUR_WHITE, asciiconsts.A_BOLD
    )
    screen.print_at("BUY", _ASCII_X_START, 1, BUY_COLOR)
    screen.print_at("SELL", _ASCII_X_START + 6, 1, SELL_COLOR)

    best_bid_str = "?" if best_bid is None else f"{best_bid:.2f}"
    best_ask_str = "?" if best_ask is None else f"{best_ask:.2f}"
    sprd = "?" if best_bid is None or best_ask is None else f"{best_ask - best_bid:.2f}"
    screen.print_at(
        f"({best_bid_str} - {best_ask_str}) Spread: {sprd}", _ASCII_X_START, 2
    )

    # print("================")
    # print(px_range)
    # print(bids_by_px)
    # print(asks_by_px)
    for y, px in enumerate(reversed(px_range)):
        color = asciiconsts.COLOUR_WHITE
        orders = None
        if px in asks:
            color = SELL_COLOR
            orders = [asks[px]]
        elif px in bids:
            color = BUY_COLOR
            orders = [bids[px]]

        # print(orders)
        # print(_format_level(px, px_decimals, orders))
        screen.print_at(
            _format_level(px, px_decimals, orders),
            _ASCII_X_START + hist_len,
            y + _ASCII_Y_START,
            color,
        )

    for idx, px in enumerate(bid_hist):
        dx = hist_len - len(bid_hist)
        if px is None:
            continue
        dy = int((highest_px - px) / px_inc)
        if dy > levels or dy < 0:
            continue
        screen.print_at("X", _ASCII_X_START + idx + dx, _ASCII_Y_START + dy, BUY_COLOR)
    for idx, px in enumerate(ask_hist):
        dx = hist_len - len(bid_hist)
        if px is None:
            continue
        dy = int((highest_px - px) / px_inc)
        if dy > levels or dy < 0:
            continue
        screen.print_at("X", _ASCII_X_START + idx + dx, _ASCII_Y_START + dy, SELL_COLOR)
    screen.refresh()