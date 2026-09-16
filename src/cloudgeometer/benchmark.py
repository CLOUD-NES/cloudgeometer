import dataclasses
import json
from collections.abc import Callable
from typing import Any

from .readers import get_reader
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

    def __len__(self) -> int:
        return len(self.runs)

    def summary(self, verbose=False) -> str:
        """Print a human-readable summary of the benchmark results."""
        return str(self.runs)

    def as_json(self) -> str:
        """Return benchmark results as a JSON-serialized string."""
        return json.dumps([dataclasses.asdict(run) for run in self.runs])


class Benchmark:
    """Setup and run a benchmark using one of the readers.

    Args:
        href (str): URL path to the dataset.
        reader (str | Callable[..., Any]): name of a registered reader (should be one
            returned by `list_readers()`), or a custom callable invoked as
            `reader(href, **reader_params)`. When a callable is supplied, no proxy/S3
            configuration is injected into it: with `log_requests=True`, only best-effort
            logging via standard proxy environment variables (e.g. `HTTPS_PROXY`,
            `CURL_CA_BUNDLE`) is applied, so libraries that don't honor those env vars
            (e.g. GDAL-, boto3-, pyarrow-based code) won't be logged.
        reader_params (dict[str, Any] | None, optional): optional parameters supported by the
            reader. For a named reader these are passed as the `params` dict to its `read()`
            method; for a custom callable they are unpacked as keyword arguments. Defaults to
            None.
        num_runs (int, optional): include this number of runs in the benchmark. Defaults to 1.
        log_requests (bool, optional): monitor and log the HTTP requests fired by the reader.
            Defaults to False.
        proxy_port (int, optional): port which the proxy used to log HTTP requests should listen to.
            Defaults to DEFAULT_PROXY_PORT.
        s3_config (S3Config | None, optional): configuration parameters for S3 access. Defaults to
            None.
    """

    def __init__(
        self,
        href: str,
        reader: str | Callable[..., Any],
        reader_params: dict[str, Any] | None = None,
        num_runs: int = 1,
        log_requests: bool = False,
        proxy_port: int = DEFAULT_PROXY_PORT,
        s3_config: S3Config | None = None,
    ):
        if not (isinstance(reader, str) or callable(reader)):
            raise TypeError(
                f"reader must be a registered reader name (str) or a callable, got {type(reader)!r}"
            )
        self.href = href
        self.reader = reader
        self.reader_params = reader_params or {}
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

    def _run_reader(self, proxy_url=None, proxy_ca_cert_file=None):
        if isinstance(self.reader, str):
            reader = get_reader(
                self.reader,
                proxy_url=proxy_url,
                proxy_ca_cert_file=proxy_ca_cert_file,
                s3_config=self.s3_config,
            )
            func = reader.read
            kwargs = {"href": self.href, "params": self.reader_params}
        else:
            # Custom callables get no proxy/S3 config injected; see class docstring.
            func = self.reader
            kwargs = {**self.reader_params, "href": self.href}
        return self._run(func=func, func_kwargs=kwargs)

    def _run_reader_with_logging(
        self,
    ) -> RunResults:
        set_proxy_env_vars = not isinstance(self.reader, str)
        with RequestLogger(port=self.proxy_port, set_proxy_env_vars=set_proxy_env_vars) as logger:
            results = self._run_reader(
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
                self._run_reader_with_logging() if self.log_requests else self._run_reader()
            )
        return BenchmarkResults(runs=runs)
