from typing import Any

from ..benchmark import Benchmark, BenchmarkResults
from ..request_logger.proxy import DEFAULT_PROXY_PORT
from ..s3 import S3Config


def run_accessor_benchmark(
    href: str,
    accessor: str,
    bbox: tuple | None = None,
    band: str | None = None,
    columns: tuple | None = None,
    group: str | None = None,
    log_requests: bool = False,
    num_runs: int = 1,
    proxy_port: int = DEFAULT_PROXY_PORT,
    s3_config: S3Config | None = None,
) -> BenchmarkResults:
    """Perform a benchmark run with the selected accessor."""
    accessor_params = _get_accessor_params(bbox=bbox, band=band, columns=columns, group=group)
    benchmark = Benchmark(
        href=href,
        accessor=accessor,
        accessor_params=accessor_params,
        log_requests=log_requests,
        num_runs=num_runs,
        proxy_port=proxy_port,
        s3_config=s3_config,
    )
    return benchmark.run()


def _get_accessor_params(**kwargs: Any) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}
