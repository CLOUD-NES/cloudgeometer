from typing import Any

import numpy as np
import xarray

from ..s3 import S3Config
from .base import BaseReader


class KerchunkReader(BaseReader):
    """Data reader based on [xarray] and [kerchunk].

    [xarray]: https://docs.xarray.dev/
    [kerchunk]: https://fsspec.github.io/kerchunk/
    """

    NAME = "kerchunk"

    def _read(self, href: str, params: dict[str, Any]) -> np.ndarray:
        """Load the full dataset, or a subset within a bounding box."""
        ds = xarray.open_dataset(
            href,
            engine="kerchunk",
            storage_options={
                "remote_options": _get_remote_options(
                    self.proxy_url, self.proxy_ca_cert_file, self.s3_config
                ),
                "target_options": _get_remote_options(
                    self.proxy_url, self.proxy_ca_cert_file, self.s3_config
                ),
                "target_protocol": "s3",
            },
        )
        da = ds["0"]  # TODO: fix hardcoded variable name
        return da.values


def _get_remote_options(
    proxy_url: str | None, proxy_ca_cert_file: str | None, s3_config: S3Config
) -> dict[str, Any]:
    """Build s3fs options for the referenced chunk data, honoring proxy and S3 configuration."""
    options: dict[str, Any] = {
        "anon": s3_config.is_anonymous,
    }
    if s3_config.access_key_id is not None:
        options["key"] = s3_config.access_key_id
    if s3_config.secret_access_key is not None:
        options["secret"] = s3_config.secret_access_key
    if s3_config.endpoint_url is not None:
        options["endpoint_url"] = s3_config.endpoint_url
    if s3_config.region is not None:
        options["client_kwargs"] = {"region_name": s3_config.region}
    if proxy_url is not None:
        config_kwargs: dict[str, Any] = {"proxies": {"http": proxy_url, "https": proxy_url}}
        if proxy_ca_cert_file is not None:
            config_kwargs["proxies_config"] = {"proxy_ca_bundle": str(proxy_ca_cert_file)}
        options["config_kwargs"] = config_kwargs
    return options
