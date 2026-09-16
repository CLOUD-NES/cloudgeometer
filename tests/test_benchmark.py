import pytest

from cloudgeometer.benchmark import Benchmark, BenchmarkResults, RunResults
from cloudgeometer.request_logger import RequestLog, RequestLogCollection


class FakeReader:
    def __init__(self, **kwargs):
        pass

    def read(self, href, params):
        return href, params


def test_benchmark_run_with_registered_reader(monkeypatch):
    monkeypatch.setattr("cloudgeometer.benchmark.get_reader", lambda name, **kwargs: FakeReader())
    benchmark = Benchmark(href="href", reader="rasterio", reader_params={"bbox": (0, 0, 1, 1)})
    results = benchmark.run()
    assert results.runs[0].success is True
    assert results.runs[0].error is None


def test_benchmark_run_with_callable_reader():
    calls = {}

    def fake_reader(href, **kwargs):
        calls["href"] = href
        calls["kwargs"] = kwargs
        return "some-data"

    benchmark = Benchmark(href="s3://bucket/key.tif", reader=fake_reader, reader_params={"foo": 1})
    results = benchmark.run()
    assert calls == {"href": "s3://bucket/key.tif", "kwargs": {"foo": 1}}
    assert results.runs[0].success is True
    assert results.runs[0].error is None


def test_benchmark_run_with_callable_reader_error_path():
    def failing_reader(href, **kwargs):
        raise ValueError("boom")

    benchmark = Benchmark(href="href", reader=failing_reader)
    results = benchmark.run()
    assert results.runs[0].success is False
    assert results.runs[0].error == "boom"


def test_benchmark_init_rejects_invalid_reader_type():
    with pytest.raises(TypeError):
        Benchmark(href="href", reader=123)


def test_log_requests_sets_proxy_env_vars_true_for_callable_reader(monkeypatch):
    captured = {}

    class FakeRequestLogger:
        def __init__(self, *args, set_proxy_env_vars=True, **kwargs):
            captured["set_proxy_env_vars"] = set_proxy_env_vars

        def __enter__(self):
            self.proxy_url = None
            self.proxy_ca_cert_file = None
            self.logs = None
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr("cloudgeometer.benchmark.RequestLogger", FakeRequestLogger)
    benchmark = Benchmark(href="href", reader=lambda href, **kw: None, log_requests=True)
    benchmark.run()
    assert captured["set_proxy_env_vars"] is True


def test_log_requests_sets_proxy_env_vars_false_for_string_reader(monkeypatch):
    captured = {}

    class FakeRequestLogger:
        def __init__(self, *args, set_proxy_env_vars=True, **kwargs):
            captured["set_proxy_env_vars"] = set_proxy_env_vars

        def __enter__(self):
            self.proxy_url = None
            self.proxy_ca_cert_file = None
            self.logs = None
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr("cloudgeometer.benchmark.RequestLogger", FakeRequestLogger)
    monkeypatch.setattr("cloudgeometer.benchmark.get_reader", lambda name, **kwargs: FakeReader())
    benchmark = Benchmark(href="href", reader="rasterio", log_requests=True)
    benchmark.run()
    assert captured["set_proxy_env_vars"] is False


def test_summarize_reports_run_and_failure_counts():
    results = BenchmarkResults(
        runs=[
            RunResults(success=True, time=1.0),
            RunResults(success=True, time=2.0),
            RunResults(success=False, time=0.5, error="boom"),
        ]
    )
    summary = results.summarize()
    assert "Runs: 3 (1 failed)" in summary


def test_summarize_time_stats_exclude_failed_runs():
    results = BenchmarkResults(
        runs=[
            RunResults(success=True, time=1.0),
            RunResults(success=True, time=2.0),
            RunResults(success=False, time=100.0, error="boom"),
        ]
    )
    summary = results.summarize()
    assert "min=1.00s, max=2.00s, avg=1.50s" in summary
    assert "100.00" not in summary


def test_summarize_warns_about_failed_runs():
    results = BenchmarkResults(
        runs=[
            RunResults(success=True, time=1.0),
            RunResults(success=False, time=0.5, error="boom"),
            RunResults(success=False, time=0.2, error="kaboom"),
        ]
    )
    summary = results.summarize()
    assert "WARNING: failed runs:" in summary
    assert "Run 2: boom" in summary
    assert "Run 3: kaboom" in summary


def test_summarize_without_request_logs_omits_request_log_section():
    results = BenchmarkResults(runs=[RunResults(success=True, time=1.0)])
    summary = results.summarize()
    assert "Request logs:" not in summary


def test_summarize_identical_request_logs_regardless_of_order():
    log_a = RequestLog(method="GET", url="http://x/a", status=200, bytes=100, range=None)
    log_b = RequestLog(method="HEAD", url="http://x/b", status=200, bytes=0, range=None)
    logs1 = RequestLogCollection([log_a, log_b])
    logs2 = RequestLogCollection([log_b, log_a])
    results = BenchmarkResults(
        runs=[
            RunResults(success=True, time=1.0, request_logs=logs1),
            RunResults(success=True, time=2.0, request_logs=logs2),
        ]
    )
    summary = results.summarize()
    assert "All runs have identical request logs." in summary
    assert "WARNING" not in summary
    assert "Requests: 2" in summary
    assert "by method: GET=1, HEAD=1" in summary
    assert "by status: 200=2" in summary
    assert "Data transferred: 100 Bytes" in summary


def test_summarize_verbose_lists_requests_only_when_identical():
    log_a = RequestLog(method="GET", url="http://x/a", status=200, bytes=100, range=None)
    logs = RequestLogCollection([log_a])
    identical_results = BenchmarkResults(
        runs=[
            RunResults(success=True, time=1.0, request_logs=logs),
            RunResults(success=True, time=1.0, request_logs=RequestLogCollection([log_a])),
        ]
    )
    summary = identical_results.summarize(verbose=True)
    assert "GET http://x/a -> 200 (100 Bytes)" in summary

    differing_results = BenchmarkResults(
        runs=[
            RunResults(success=True, time=1.0, request_logs=logs),
            RunResults(
                success=True,
                time=1.0,
                request_logs=RequestLogCollection(
                    [
                        RequestLog(
                            method="GET", url="http://x/c", status=206, bytes=50, range="bytes=0-49"
                        )
                    ]
                ),
            ),
        ]
    )
    summary = differing_results.summarize(verbose=True)
    assert "GET http://x/a -> 200" not in summary


def test_summarize_warns_when_request_logs_differ():
    log_a = RequestLog(method="GET", url="http://x/a", status=200, bytes=100, range=None)
    log_c = RequestLog(method="GET", url="http://x/c", status=206, bytes=50, range="bytes=0-49")
    results = BenchmarkResults(
        runs=[
            RunResults(success=True, time=1.0, request_logs=RequestLogCollection([log_a])),
            RunResults(success=True, time=1.0, request_logs=RequestLogCollection([log_c])),
        ]
    )
    summary = results.summarize()
    assert "WARNING: request logs differ across runs." in summary
    assert "Run 1:" in summary
    assert "Run 2:" in summary
    assert "by status: 200=1" in summary
    assert "by status: 206=1" in summary
