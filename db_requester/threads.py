import math
from itertools import repeat
from queue import Queue


class ThreadCounter:
    """A simple approach to scheduling forever-blocking threads."""

    def __init__(self, count: int) -> None:
        self._count = count

    def one(self) -> bool:
        if self._count == 0:
            return False
        self._count -= 1
        return True

    def pool(self, worker_pools: int) -> int:
        rounded_down_division = math.floor(self._count / worker_pools)
        remainder = self._count % worker_pools
        self._count = 0
        return [
            *repeat(rounded_down_division + 1, remainder),
            *repeat(rounded_down_division, worker_pools - remainder),
        ]


class IterableQueue(Queue):
    _sentinel = object()

    def __iter__(self):
        return iter(self.get, self._sentinel)

    def close(self):
        self.put(self._sentinel)
