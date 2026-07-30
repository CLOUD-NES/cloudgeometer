import time
from typing import Self


class Timer:
    def __enter__(self) -> Self:
        self._t0: float = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.elapsed_time: float = time.perf_counter() - self._t0
        del self._t0
