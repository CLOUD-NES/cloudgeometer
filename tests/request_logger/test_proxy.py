import socket

import pytest

from cloudgeometer.request_logger import proxy


def test_find_free_port_skips_busy_port():
    with socket.create_server(("127.0.0.1", 0)) as other:
        busy = other.getsockname()[1]
        assert proxy._find_free_port("127.0.0.1", default=busy) != busy


def test_proxy_generates_default_ca_cert(tmp_path, monkeypatch):
    ca_cert = tmp_path / ".mitmproxy" / "mitmproxy-ca-cert.pem"
    monkeypatch.setattr(proxy, "DEFAULT_CA_CERT", ca_cert)
    assert proxy.Proxy().ca_cert == ca_cert
    assert ca_cert.exists()


def test_proxy_raises_if_custom_ca_cert_is_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        proxy.Proxy(ca_cert=tmp_path / "missing.pem")
