import dataclasses
import json
from collections.abc import Callable
from typing import Any

from .accessors import get_accessor
from .request_logger import RequestLogCollection, RequestLogger
from .request_logger.proxy import DEFAULT_PROXY_PORT
from .s3 import S3Config
from .timer import Timer


@dataclasses.dataclass
class RunResults:
    """Results of a benchmark run."""

    success: bool
    time: float | None = None
    request_logs: RequestLogCollection | None = None
    error: str | None = None


@dataclasses.dataclass(frozen=True)
class BenchmarkResults:
    """Results of a benchmark.

    A benchmark can entails several runs.
    """

    runs: list[RunResults] = dataclasses.field(default_factory=list)

    def __len__(self):
        return len(self.runs)

    def summary(self, verbose=False) -> str:
        """Print a human-readable summary of the benchmark results."""
        return str(self.runs)

    def as_json(self) -> str:
        """Return benchmark results as a JSON-serialized string."""
        return json.dumps([dataclasses.asdict(run) for run in self.runs])


class Benchmark:
    """Setup and run a benchmark using one of the accessors.

    Args:
        href (str): URL path to the dataset.
        accessor (str): name of the accessor (should be one returned by `list_accessors()`).
        accessor_params (dict[str, Any] | None, optional): optional parameters supported by the
            accessor. Defaults to None.
        num_runs (int, optional): include this number of runs in the benchmark. Defaults to 1.
        log_requests (bool, optional): monitor and log the HTTP requests fired by the accessor.
            Defaults to False.
        proxy_port (int, optional): port which the proxy used to log HTTP requests should listen to.
            Defaults to DEFAULT_PROXY_PORT.
        s3_config (S3Config | None, optional): configuration parameters for S3 access. Defaults to
            None.
    """

    def __init__(
        self,
        href: str,
        accessor: str,
        accessor_params: dict[str, Any] | None = None,
        num_runs: int = 1,
        log_requests: bool = False,
        proxy_port: int = DEFAULT_PROXY_PORT,
        s3_config: S3Config | None = None,
    ):
        self.href = href
        self.accessor = accessor
        self.accessor_params = accessor_params or {}
        self.num_runs = num_runs
        self.log_requests = log_requests
        self.proxy_port = proxy_port
        self.s3_config = s3_config or S3Config()

    # @staticmethod
    def _run(self, func: Callable, func_kwargs: dict[str, Any]) -> RunResults:
        error = None
        with Timer() as timer:
            try:
                _ = func(**func_kwargs)
            except Exception as e:
                error = str(e)
        return RunResults(
            success=error is None,
            time=timer.elapsed_time,
            error=error,
        )

    def _run_accessor(self, proxy_url=None, proxy_ca_cert_file=None):
        accessor = get_accessor(
            self.accessor,
            proxy_url=proxy_url,
            proxy_ca_cert_file=proxy_ca_cert_file,
            s3_config=self.s3_config
        )
        kwargs = {"href": self.href, "params": self.accessor_params}
        results = self._run(func=accessor.run, func_kwargs=kwargs)
        return results


    def _run_accessor_with_request_logger(
        self,
    ) -> RunResults:
        with RequestLogger(port=self.proxy_port, set_proxy_env_vars=False) as logger:
            results = self._run_accessor(
                proxy_url=logger.proxy_url, proxy_ca_cert_file=logger.proxy_ca_cert_file
            )
        results.request_logs = logger.logs
        return results

    def run(self):
        """Run the benchmark.

        Returns:
            BenchmarkResults: results of the benchmark.
        """
        runs = []
        for _ in range(self.num_runs):
            runs.append(
                self._run_accessor_with_request_logger() if self.log_requests else self._run_accessor()
            )
        return BenchmarkResults(runs=runs)
