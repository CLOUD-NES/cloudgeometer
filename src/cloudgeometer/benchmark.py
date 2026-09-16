import dataclasses
import json
from collections import Counter
from collections.abc import Callable
from typing import Any

from .readers import get_reader
from .request_logger import RequestLogCollection, RequestLogger
from .request_logger.proxy import DEFAULT_PROXY_PORT
from .s3 import S3Config
from .timer import Timer
from .utils import as_human_readable_size


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

    def __repr__(self) -> str:
        num_failed_runs = len([r for r in self.runs if not r.success])
        return f"<BenchmarkResults: {len(self)} runs ({num_failed_runs} failed)>"

    def summarize(self, verbose: bool = False) -> str:
        """Return a human-readable summary of the benchmark results."""
        failed_runs = [(i, r.error) for i, r in enumerate(self.runs, start=1) if not r.success]
        lines = [
            f"Runs: {len(self)} ({len(failed_runs)} failed)",
        ]
        if failed_runs:
            lines.append("WARNING: failed runs:")
            for i, error in failed_runs:
                lines.append(f"  Run {i}: {error}")

        times = [r.time for r in self.runs if r.success and r.time is not None]
        if times:
            lines.append("")
            lines.append(
                f"Execution time (successful runs only): "
                f"min={min(times):.2f}s, max={max(times):.2f}s, avg={sum(times) / len(times):.2f}s"
            )

        logs_by_run = [r.request_logs for r in self.runs if r.request_logs is not None]
        if logs_by_run:
            lines.append("")
            lines.extend(self._summarize_request_logs(logs_by_run, verbose=verbose))

        return "\n".join(lines)

    @staticmethod
    def _format_log_stats(logs: RequestLogCollection, indent: str = "") -> list[str]:
        by_method = Counter(log.method for log in logs.request_logs)
        by_status = Counter(log.status for log in logs.request_logs)
        return [
            f"{indent}Requests: {len(logs)}",
            f"{indent}  by method: " + ", ".join(f"{m}={n}" for m, n in sorted(by_method.items())),
            f"{indent}  by status: " + ", ".join(f"{s}={n}" for s, n in sorted(by_status.items())),
            f"{indent}Data transferred: {as_human_readable_size(logs.total_bytes)}",
        ]

    def _summarize_request_logs(
        self, logs_by_run: list[RequestLogCollection], verbose: bool
    ) -> list[str]:
        lines = ["Request logs:"]
        signatures = [Counter(logs.request_logs) for logs in logs_by_run]
        identical = all(sig == signatures[0] for sig in signatures[1:])

        if identical:
            lines.append("  All runs have identical request logs.")
            lines.extend(self._format_log_stats(logs_by_run[0], indent="  "))
            if verbose:
                lines.append("  Requests:")
                for log in logs_by_run[0].request_logs:
                    range_info = f", range={log.range}" if log.range else ""
                    lines.append(
                        f"    {log.method} {log.url} -> {log.status} "
                        f"({as_human_readable_size(log.bytes)}{range_info})"
                    )
        else:
            lines.append("  WARNING: request logs differ across runs.")
            for i, logs in enumerate(logs_by_run, start=1):
                lines.append(f"  Run {i}:")
                lines.extend(self._format_log_stats(logs, indent="    "))

        return lines

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
