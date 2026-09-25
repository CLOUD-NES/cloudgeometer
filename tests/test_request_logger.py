import http.server
import socket
import threading
import urllib.request

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


def test_request_logger_keeps_logs_exceeding_queue_pipe_size(tmp_path):
    # Start a local HTTP server and sends 100 plain-HTTP requests through the proxy
    ca_cert = tmp_path / "ca-cert.pem"
    ca_cert.touch()
    with http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0), http.server.SimpleHTTPRequestHandler
    ) as server:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        # ~100 kB of logs overflows the queue pipe (~64 kB), which used to hang the proxy exit
        url = f"http://127.0.0.1:{server.server_port}/{'x' * 1000}"
        n = 100
        with RequestLogger(set_proxy_env_vars=False, ca_cert=ca_cert) as logger:
            opener = urllib.request.build_opener(
                urllib.request.ProxyHandler({"http": logger.proxy_url})
            )
            for _ in range(n):
                with pytest.raises(urllib.error.HTTPError):  # 404, but still logged
                    opener.open(url)
        server.shutdown()
    assert len(logger.logs) == n
