import asyncio
import contextlib
import dataclasses
import multiprocessing
import multiprocessing.synchronize
import pathlib
import queue
import socket
import threading
import time

from mitmproxy import addons, http, master, options

DEFAULT_PROXY_PORT = 8080
DEFAULT_CA_CERT = pathlib.Path.home() / ".mitmproxy" / "mitmproxy-ca-cert.pem"


@dataclasses.dataclass(frozen=True)
class RequestLog:
    """A logged HTTP request/response."""

    method: str
    url: str
    status: int
    bytes: int
    range: str | None


class _Master(master.Master):
    """The master handles mitmproxy's main event loop.

    This implementation already register the default addons.
    """

    def __init__(
        self,
        options: options.Options,
        loop: asyncio.AbstractEventLoop | None = None,
        with_termlog: bool = True,
    ) -> None:
        super().__init__(options, event_loop=loop, with_termlog=with_termlog)
        self.addons.add(*addons.default_addons())


class _RequestLogger:
    """mitmproxy addon to log HTTP requests.

    Information extracted from the requests/responses are added to a multiprocessing.Queue, so that
    they can be accessed from another process. The addon supports an optional filter to selectively
    monitor a given host.
    """

    def __init__(self, queue: multiprocessing.Queue, host_filter: str = "") -> None:
        self.host_filter = host_filter
        self.queue = queue

    def response(self, flow: http.HTTPFlow) -> None:
        if self.host_filter not in flow.request.pretty_host:
            return
        assert flow.response is not None
        self.queue.put(
            RequestLog(
                method=flow.request.method,
                url=flow.request.pretty_url,
                status=flow.response.status_code,
                bytes=len(flow.response.raw_content or b""),
                range=flow.request.headers.get("Range"),
            )
        )


class _ProxyProcess(multiprocessing.Process):
    def __init__(
            self,
            host: str,
            port: int,
            host_filter: str,
            stop: multiprocessing.synchronize.Event,
            queue: multiprocessing.Queue,
    ) -> None:
        self.host = host
        self.port = port
        self.host_filter = host_filter
        self.stop = stop
        self.queue = queue
        super().__init__(daemon=True)

    async def _run(self) -> None:
        request_logger = _RequestLogger(self.queue, host_filter=self.host_filter)
        opts = options.Options(listen_host=self.host, listen_port=self.port)
        master = _Master(opts, with_termlog=False)
        master.addons.add(request_logger)

        def _watch_stop() -> None:
            self.stop.wait()
            master.shutdown()

        threading.Thread(target=_watch_stop, daemon=True).start()

        await master.run()

    def run(self) -> None:
        asyncio.run(self._run())


class Proxy:

    host: str = "127.0.0.1"

    def __init__(
            self,
            host_filter: str = "",
            port: int | None = None,
            ca_cert: str | pathlib.Path | None = None,
    ) -> None:
        self.host_filter: str = host_filter
        self.port: int = DEFAULT_PROXY_PORT if port is None else port
        self.ca_cert: pathlib.Path = DEFAULT_CA_CERT if ca_cert is None else pathlib.Path(ca_cert)
        if not self.ca_cert.exists():
            raise FileNotFoundError(
                f"mitmproxy CA certificate not found at {self.ca_cert}. "
                "Run `mitmdump` once (Ctrl+C after a second) to generate it."
            )
        self._process: multiprocessing.Process | None = None
        self._stop: multiprocessing.synchronize.Event | None = None
        self._queue: multiprocessing.Queue = multiprocessing.Queue()
        self._request_logs: list[RequestLog] = []

    def start(self) -> None:
        self._stop = multiprocessing.Event()
        self._process = _ProxyProcess(
            self.host,
            self.port,
            self.host_filter,
            self._stop,
            self._queue,
        )
        self._process.start()
        self._wait_until_listening()

    def _wait_until_listening(self, timeout: float = 5.0) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self._process is not None and not self._process.is_alive():
                raise RuntimeError(
                    f"mitmproxy exited early with code {self._process.exitcode}"
                )
            with (
                contextlib.suppress(OSError),
                socket.create_connection((self.host, self.port), timeout=0.2),
            ):
                return
            time.sleep(0.05)
        raise RuntimeError("mitmproxy did not start listening in time")

    def stop(self) -> None:
        if self._stop is not None:
            self._stop.set()
        if self._process is not None:
            self._process.join(timeout=5)
            if self._process.is_alive():
                self._process.terminate()
                self._process.join(timeout=5)
            self._process = None

    @property
    def request_logs(self) -> list[RequestLog]:
        request_logs = self._drain_queue()
        if request_logs:
            self._request_logs.extend(request_logs)
        return self._request_logs

    def _drain_queue(self) -> list[RequestLog]:
        logs: list[RequestLog] = []
        while True:
            try:
                logs.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return logs

    @property
    def url(self) -> str:
        """Proxy URL."""
        return f"http://{self.host}:{self.port}"

