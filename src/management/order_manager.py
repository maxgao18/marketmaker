def filter_order_ids(
    symbol,
    state,
    order_types=None,
    timestamp_filter_func=lambda ts: True,
    px_filter_func=lambda px: True,
    remove_in_flight_canceled=True,
):
    filtered_orders = set()
    for id, o in state.portfolio.outstanding_orders(symbol).items():
        if order_types is not None and o["type"] in order_types:
            continue
        elif "recv_time" in o and not timestamp_filter_func(o["recv_time"]):
            continue
        elif "px" in o and not px_filter_func(o["px"]):
            continue
        filtered_orders.add(id)

    in_flight_cancels = []
    if remove_in_flight_canceled:
        for o in state.portfolio.in_flight_orders(symbol).values():
            otype = o["type"]
            if otype == "CANCEL":
                in_flight_cancels.append(o["order_id"])
            elif otype == "CANCELALL" and isinstance(o["order_ids"], list):
                in_flight_cancels += o["order_ids"]

    to_cancel = set(filtered_orders).difference(in_flight_cancels)
    return to_cancel
