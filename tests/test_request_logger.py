import socket

import pytest

from cloudgeometer import RequestLogger
from cloudgeometer.request_logger.proxy import _find_free_port


def test_request_logger_raises_if_port_is_busy(tmp_path):
    ca_cert = tmp_path / "ca-cert.pem"
    ca_cert.touch()
    # simulate another user/process listening on the proxy port
    with socket.create_server(("127.0.0.1", 0)) as other:
        port = other.getsockname()[1]
        with (
            pytest.raises(RuntimeError, match="exited early"),
            RequestLogger(set_proxy_env_vars=False, ca_cert=ca_cert, port=port),
        ):
            pass


def test_find_free_port_skips_busy_port():
    with socket.create_server(("127.0.0.1", 0)) as other:
        busy = other.getsockname()[1]
        assert _find_free_port("127.0.0.1", default=busy) != busy
