from pathlib import Path
from typing import Any

import geopandas
import pyarrow.fs

from ..s3 import S3Config
from .base import BaseReader

DEFAULT_REQUEST_TIMEOUT = 20  # seconds


class GeopandasPyarrowReader(BaseReader):
    """Data loader based on [geopandas.read_parquet], which is based on [pyarrow].

    [geopandas.read_parquet]: https://geopandas.org/en/stable/docs/reference/api/geopandas.read_parquet.html
    [pyarrow]: https://arrow.apache.org/docs/python/index.html
    """

    NAME: str = "geopandas-pyarrow"
    PARAMS: tuple = ("bbox", "columns")

    def _read(self, href: str, params: dict[str, Any]) -> geopandas.GeoDataFrame:
        """Load the dataset or a subset of columns, optionally filtering using a bounding box."""
        # if the pyarrow filesystem is passed to geopandas, strip the protocol and any leading "/"
        href, filesystem = _setup_filesystem_if_s3(
            href,
            proxy_url=self.proxy_url,
            proxy_ca_file_path=self.proxy_ca_cert_file,
            s3_config=self.s3_config,
        )
        bbox: tuple | None = params.get("bbox")
        columns: tuple | None = params.get("columns")
        return geopandas.read_parquet(href, bbox=bbox, columns=columns, filesystem=filesystem)


def _setup_filesystem_if_s3(
    href: str, proxy_url: str | None, proxy_ca_file_path: Path | None, s3_config: S3Config
) -> tuple[str, pyarrow.fs.S3FileSystem | None]:
    if href.startswith("s3://"):
        filesystem = _get_pyarrow_s3_filesystem(proxy_url, proxy_ca_file_path, s3_config)
        return href[5:], filesystem  # if using a pyarrow filesystem, strip protocol and leading "/"
    else:
        return href, None


def _get_pyarrow_s3_filesystem(
    proxy_url: str | None, proxy_ca_file_path: Path | None, s3_config: S3Config
) -> pyarrow.fs.S3FileSystem:
    return pyarrow.fs.S3FileSystem(
        access_key=s3_config.access_key_id,
        secret_key=s3_config.secret_access_key,
        anonymous=s3_config.is_anonymous,
        region=s3_config.region,
        endpoint_override=s3_config.endpoint_url,
        proxy_options=proxy_url,
        tls_ca_file_path=str(proxy_ca_file_path) if proxy_ca_file_path is not None else None,
        request_timeout=DEFAULT_REQUEST_TIMEOUT,
    )
