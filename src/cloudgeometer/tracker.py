import os
from pathlib import Path
from types import TracebackType
from typing import Self

from .proxy import Proxy, RequestLog


class RequestTracker:
    """Track HTTP/HTTPS requests."""

    def __init__(
        self,
        host_filter: str = "",
        ca_cert: str | Path | None = None,
        port: int | None = None,
    ) -> None:
        self._proxy = Proxy(
            host_filter=host_filter,
            port=port,
            ca_cert=ca_cert,
        )
        self._old_env: dict[str, str | None] = {}

    def __enter__(self) -> Self:
        self._proxy.start()
        self._set_env()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._restore_env()
        self._proxy.stop()

    def _set_env(self) -> None:
        proxy_url = self._proxy.url
        ca_cert_file = str(self._proxy.ca_cert)
        ca_cert_dir = str(self._proxy.ca_cert.parent)
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
        return self._proxy.request_logs

    @property
    def total_bytes(self) -> int:
        """Total response bytes across all logged requests."""
        return sum(r.bytes for r in self.request_logs)


