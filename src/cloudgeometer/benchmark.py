import contextlib
import logging
from dataclasses import dataclass
from typing import Any

from .accessors import get_accessor
from .timer import Timer
from .tracker import RequestLog, RequestTracker

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BenchmarkResult:
    success: bool
    time: float | None = None
    request_logs: list[RequestLog] | None = None
    error: str | None = None

    def summary(self, verbose=True) -> None:
        """Print a human-readable summary of the benchmark results."""
        if self.success:
            print("Successful run.")
        else:
            print(f"Failed with error:\n{self.error}")
            return
        if self.time is not None:
            print(f"Timing: {self.time}")
        if self.request_logs is not None:
            num_requests = len(self.request_logs)
            total_bytes = sum([r.bytes for r in self.request_logs])
            print(f"{num_requests} requests, {total_bytes} bytes transferred")
            if verbose:
                for r in self.request_logs:
                    range_part = f" range={r.range}" if r.range else ""
                    print(f"  {r.method:5s} {r.status} {r.bytes:>10d}B{range_part}  {r.url}")


class Benchmark:
    def __init__(
        self,
        id: str,
        href: str,
        accessor: str,
        network_stats: bool = False,
        accessor_params: dict[str, Any] | None = None,
        proxy_port: int | None = None,
    ):
        self.id = id
        self.href = href
        self.accessor = accessor
        self.network_stats = network_stats
        self.accessor_params = accessor_params or {}
        self.proxy_port = proxy_port
        self.result: BenchmarkResult | None = None

    def _run(self):
        accessor = get_accessor(self.accessor, href=self.href, params=self.accessor_params)

        # TODO: implement host filter?
        cm = (
            RequestTracker(port=self.proxy_port) if self.network_stats else contextlib.nullcontext()
        )

        with cm as tracker, Timer() as timer:
            try:
                data = accessor.load()
                print(data)
            except Exception as e:
                return BenchmarkResult(
                    success=False,
                    error=str(e),
                )
        return BenchmarkResult(
            success=True,
            time=timer.elapsed_time,
            request_logs=tracker.request_logs if tracker is not None else None,
        )

    def run(self):
        """Run the benchmark."""
        self.result = self._run()

    def summary(self):
        """Print a summary of the benchmark.

        Requires `Benchmark.run` to be called first.
        """
        if self.result:
            self.result.summary()
        else:
            logger.warning("Benchmark contains no result yet. Call `Benchmark.run` first.")
