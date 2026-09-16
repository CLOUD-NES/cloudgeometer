from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping
from typing import Any

from ..s3 import S3Config


class BaseReader(ABC):
    """Base class for the data readers.

    Derived classes should implement the argument-free `_read` function. In order to provide
    parameters to the reader, use the `params` argument (the `PARAMS` class attribute should list
    the parameters supported by the reader). The `NAME` attribute defines the name of the reader.
    """

    NAME: str = "base"
    PARAMS: tuple = ()

    def __init__(
        self,
        proxy_url: str | None = None,
        proxy_ca_cert_file: str | None = None,
        s3_config: S3Config | None = None,
    ) -> None:
        self.proxy_url = proxy_url
        self.proxy_ca_cert_file = proxy_ca_cert_file
        self.s3_config = s3_config or S3Config()

    @classmethod
    def check_params(cls, params: str | Iterable[str] | Mapping):
        """Check whether the class implements one or multiple parameters for reading."""
        if isinstance(params, str):
            params = (params,)
        elif isinstance(params, Mapping):
            params = params.keys()
        for p in params:
            if p not in cls.PARAMS:
                raise ValueError(f"Parameter {p} not supported by reader {cls.NAME}")

    @abstractmethod
    def _read(self, href: str, params: dict[str, Any]) -> Any:
        """Actual data reader implementation."""
        ...

    def read(self, href: str, params: dict[str, Any]) -> Any:
        """Read the dataset, with some optional filters/configuration parameters."""
        self.check_params(params=params)
        return self._read(href=href, params=params)
