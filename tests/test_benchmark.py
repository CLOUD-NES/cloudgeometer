import pytest

from cloudgeometer.benchmark import Benchmark


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
