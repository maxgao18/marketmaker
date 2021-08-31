def idx_of_next_largest_backwards_search(lst, v):
    if lst is None or len(lst) == 0:
        return -1
    if lst[0] > v:
        return 0

    for i in range(1, len(lst) + 1):
        if lst[-i] <= v:
            return len(lst) + 1 - i
    return -1
