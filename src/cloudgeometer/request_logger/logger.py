import os
from pathlib import Path
from types import TracebackType
from typing import Self

from .log import RequestLogCollection
from .proxy import Proxy


class RequestLogger:
    """Track HTTP/HTTPS requests."""

    def __init__(
        self,
        host_filter: str = "",
        set_proxy_env_vars: bool = True,
        ca_cert: str | Path | None = None,
        port: int | None = None,
    ) -> None:
        self._proxy = Proxy(
            host_filter=host_filter,
            port=port,
            ca_cert=ca_cert,
        )
        self.set_proxy_env_vars = set_proxy_env_vars
        self._old_env: dict[str, str | None] = {}

    def __enter__(self) -> Self:
        self._proxy.start()
        if self.set_proxy_env_vars:
            self._set_env()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self.set_proxy_env_vars:
            self._restore_env()
        self._proxy.stop()

    def _set_env(self) -> None:
        proxy_url = self.proxy_url
        ca_cert_file = str(self.proxy_ca_cert_file)
        ca_cert_dir = str(self.proxy_ca_cert_file.parent)
        updates = {
            "HTTP_PROXY": self.proxy_url,
            "HTTPS_PROXY": self.proxy_url,
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
    def proxy_url(self) -> str:
        """URL address of the proxy."""
        return self._proxy.url

    @property
    def proxy_ca_cert_file(self) -> Path:
        """Location of the proxy trusted CA certificates."""
        return self._proxy.ca_cert

    @property
    def logs(self) -> RequestLogCollection:
        """Logs of the tracked requests."""
        return self._proxy.request_logs
