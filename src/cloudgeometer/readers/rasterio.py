from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import numpy as np
import rasterio
from rasterio.windows import from_bounds

from ..s3 import S3Config
from .base import BaseReader


class RasterioReader(BaseReader):
    """Data reader based on [rasterio].

    [rasterio]: https://rasterio.readthedocs.io
    """

    NAME: str = "rasterio"
    PARAMS: tuple = ("bbox",)

    def _read(self, href: str, params: dict[str, Any]) -> np.ndarray:
        """Load the full dataset, or a subset within a bounding box."""
        kwargs = {}
        bbox = params.get("bbox")
        with (
            rasterio_env(self.proxy_url, self.proxy_ca_cert_file, self.s3_config),
            rasterio.open(href) as dataset,
        ):
            if bbox is not None:
                kwargs["window"] = from_bounds(*bbox, transform=dataset.transform)
            return dataset.read(**kwargs)


@contextmanager
def rasterio_env(
    proxy_url: str | None, proxy_ca_file_path: str | None, s3_config: S3Config
) -> Generator[None]:
    """Set up the rasterio environment, including proxy and S3 configurations.

    Args:
        proxy_url (str | None): URL address of the proxy for request logging
        proxy_ca_file_path (str | None): path to the proxy certificates
        s3_config (S3Config): configuration parameters for S3 access

    Yields:
        None: control is yielded within the configured rasterio environment
    """
    env = {
        "GDAL_DISABLE_READDIR_ON_OPEN": True,
        "AWS_NO_SIGN_REQUEST": "YES" if s3_config.is_anonymous else "NO",
    }
    if proxy_url is not None:
        env["GDAL_HTTPS_PROXY"] = proxy_url
    if proxy_ca_file_path is not None:
        env["GDAL_CURL_CA_BUNDLE"] = proxy_ca_file_path
    if s3_config.access_key_id is not None:
        env["AWS_ACCESS_KEY_ID"] = s3_config.access_key_id
    if s3_config.secret_access_key is not None:
        env["AWS_SECRET_ACCESS_KEY"] = s3_config.secret_access_key
    if s3_config.region is not None:
        env["AWS_REGION"] = s3_config.region
    if s3_config.endpoint_url is not None:
        env["AWS_S3_ENDPOINT"] = s3_config.endpoint_url
    with rasterio.Env(**env):
        yield
