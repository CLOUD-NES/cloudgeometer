from typing import Any

from ..benchmark import Benchmark, BenchmarkResults
from ..s3 import S3Config


def run_reader_benchmark(
    href: str,
    reader: str,
    bbox: tuple | None = None,
    band: str | None = None,
    columns: tuple | None = None,
    group: str | None = None,
    log_requests: bool = False,
    num_runs: int = 1,
    proxy_port: int | None = None,
    s3_config: S3Config | None = None,
) -> BenchmarkResults:
    """Perform a benchmark run with the selected reader."""
    reader_params = _get_reader_params(bbox=bbox, band=band, columns=columns, group=group)
    benchmark = Benchmark(
        href=href,
        reader=reader,
        reader_params=reader_params,
        log_requests=log_requests,
        num_runs=num_runs,
        proxy_port=proxy_port,
        s3_config=s3_config,
    )
    return benchmark.run()


def _get_reader_params(**kwargs: Any) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}
