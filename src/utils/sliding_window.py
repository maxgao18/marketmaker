from collections import deque


class SlidingWindow:
    def __init__(self, thres):
        self._thres = thres
        self.indexes = deque()
        self.values = deque()

    def append(self, value, index=None):
        while (
            self._thres > 0
            and len(self.indexes) > 0
            and index - self.indexes[0] > self._thres
        ):
            self.values.popleft()
            self.indexes.popleft()

        if index is None:
            index = self.indexes[-1] + 1 if len(self.indexes) > 0 else 0
        self.values.append(value)
        self.indexes.append(index)

    def clear(self):
        self.indexes.clear()
        self.values.clear()

    def __len__(self):
        return len(self.values)

    def __getitem__(self, arg):
        return self.values[arg]
