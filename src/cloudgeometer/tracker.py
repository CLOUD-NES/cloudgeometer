import asyncio
import contextlib
import os
import socket
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from mitmproxy import http, options
from mitmproxy.tools.dump import DumpMaster

DEFAULT_PROXY_PORT = 8080
DEFAULT_CA_CERT = Path.home() / ".mitmproxy" / "mitmproxy-ca-cert.pem"


@dataclass(frozen=True)
class RequestLog:
    """A logged HTTP request/response."""

    method: str
    url: str
    status: int
    bytes: int
    range: str | None


class _RequestRecorder:
    def __init__(self, host_filter: str = "") -> None:
        self.host_filter = host_filter
        self.request_logs: list[RequestLog] = []

    def response(self, flow: http.HTTPFlow) -> None:
        if self.host_filter not in flow.request.pretty_host:
            return
        assert flow.response is not None
        self.request_logs.append(
            RequestLog(
                method=flow.request.method,
                url=flow.request.pretty_url,
                status=flow.response.status_code,
                bytes=len(flow.response.raw_content or b""),
                range=flow.request.headers.get("Range"),
            )
        )


class RequestTracker:
    """Track HTTP/HTTPS requests."""

    def __init__(
        self,
        host_filter: str = "",
        ca_cert: Path = DEFAULT_CA_CERT,
        port: int | None = None,
    ) -> None:
        self.ca_cert = Path(ca_cert)
        if not ca_cert.exists():
            raise FileNotFoundError(
                f"mitmproxy CA certificate not found at {self.ca_cert}. "
                "Run `mitmdump` once (Ctrl+C after a second) to generate it."
            )
        self.recorder = _RequestRecorder(host_filter)
        self._host = "127.0.0.1"
        self._port = port or DEFAULT_PROXY_PORT
        self._master: DumpMaster | None = None
        self._thread: threading.Thread | None = None
        self._old_env: dict[str, str | None] = {}

    def __enter__(self) -> Self:
        self._start_proxy()
        self._set_env()
        return self

    def __exit__(self, exc_type, exc_val, traceback) -> None:
        self._restore_env()
        self._stop_proxy()

    def _start_proxy(self) -> None:
        ready = threading.Event()

        def _run() -> None:
            asyncio.run(self._amain(ready))

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()
        if not ready.wait(timeout=5):
            raise RuntimeError("mitmproxy failed to start")
        self._wait_until_listening()

    async def _amain(self, ready: threading.Event) -> None:
        opts = options.Options(listen_host=self._host, listen_port=self._port)
        self._master = DumpMaster(opts, with_termlog=False, with_dumper=False)
        self._master.addons.add(self.recorder)
        ready.set()
        await self._master.run()

    def _wait_until_listening(self, timeout: float = 5.0) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            with (
                contextlib.suppress(OSError),
                socket.create_connection((self._host, self._port), timeout=0.2),
            ):
                return
            time.sleep(0.05)
        raise RuntimeError("mitmproxy did not start listening in time")

    def _stop_proxy(self) -> None:
        if self._master is not None:
            # DumpMaster.shutdown() stops the run loop but never closes the
            # listening socket (Proxyserver has no shutdown hook), so the
            # port stays bound until we close it explicitly.
            proxyserver = self._master.addons.get("proxyserver")
            if proxyserver is not None:
                future = asyncio.run_coroutine_threadsafe(
                    proxyserver.servers.update([]), self._master.event_loop
                )
                with contextlib.suppress(Exception):
                    future.result(timeout=5)
            self._master.shutdown()
        if self._thread is not None:
            self._thread.join(timeout=5)
        self._master = None

    def _set_env(self) -> None:
        proxy_url = f"http://{self._host}:{self._port}"
        ca_cert_file = str(self.ca_cert)
        ca_cert_dir = str(self.ca_cert.parent)
        updates = {
            "HTTP_PROXY": proxy_url,
            "HTTPS_PROXY": proxy_url,
            "http_proxy": proxy_url,
            "https_proxy": proxy_url,
            "SSL_CERT_DIR": ca_cert_dir,
            "SSL_CERT_FILE": ca_cert_file,
            "CURL_CA_BUNDLE": ca_cert_file,
            "REQUESTS_CA_BUNDLE": ca_cert_file,
            "GDAL_CURL_CA_BUNDLE": ca_cert_file,
        }
        self._old_env = {key: os.environ.get(key) for key in updates}
        os.environ.update(updates)

    def _restore_env(self) -> None:
        for key, value in self._old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    @property
    def request_logs(self) -> list[RequestLog]:
        """Logged requests."""
        return self.recorder.request_logs

    @property
    def total_bytes(self) -> int:
        """Total response bytes across all logged requests."""
        return sum(r.bytes for r in self.request_logs)

    def summary(self) -> str:
        """Return a human-readable summary of logged requests and bytes."""
        lines = [f"{len(self.request_logs)} requests, {self.total_bytes} bytes transferred"]
        for r in self.request_logs:
            range_part = f" range={r.range}" if r.range else ""
            lines.append(f"  {r.method:5s} {r.status} {r.bytes:>10d}B{range_part}  {r.url}")
        return "\n".join(lines)
