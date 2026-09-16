import asyncio
import pathlib
from typing import Any
from urllib.parse import urlsplit

import numpy as np
from async_geotiff import GeoTIFF
from obstore.store import LocalStore, ObjectStore, S3Store

from ..s3 import S3Config
from .base import BaseReader


async def _async_geotiff_read(
    prefix: str, store: ObjectStore, bbox: tuple[float, float, float, float] | None = None
) -> np.ndarray:
    geotiff = await GeoTIFF.open(prefix, store=store)
    if bbox:
        raise NotImplementedError()
    array = await geotiff.read()
    return array.data


class AsyncGeotiffReader(BaseReader):
    """Data reader based on [async-geotiff][async-geotiff].

    [async-geotiff]: https://developmentseed.org/async-geotiff
    """

    NAME = "async-geotiff"

    def _read(self, href: str, params: dict[str, Any]) -> np.ndarray:
        """Load the full dataset, or a subset within a bounding box."""
        store, prefix = _set_up_store_and_prefix(
            href=href,
            proxy_url=self.proxy_url,
            proxy_ca_cert_file=self.proxy_ca_cert_file,
            s3_config=self.s3_config,
        )
        return asyncio.run(_async_geotiff_read(prefix, store))


def _set_up_store_and_prefix(
    href: str, proxy_url: str | None, proxy_ca_cert_file: pathlib.Path | None, s3_config: S3Config
) -> tuple[ObjectStore, str]:
    href_split = urlsplit(href)
    scheme = href_split.scheme
    if not scheme or scheme == "file":
        # local store configuration, no need for proxy
        return LocalStore(href), pathlib.Path(href_split.path).as_uri()
    elif scheme == "s3":
        # s3 store configuration
        s3_options = {}
        if s3_config.access_key_id is not None:
            s3_options["access_key_id"] = s3_config.access_key_id
        if s3_config.secret_access_key is not None:
            s3_options["secret_access_key"] = s3_config.secret_access_key
        if s3_config.endpoint_url is not None:
            s3_options["endpoint"] = s3_config.endpoint_url
        if s3_config.region is not None:
            s3_options["region"] = s3_config.region
        s3_options["skip_signature"] = s3_config.is_anonymous

        # if available, also add proxy configuration
        client_options = {}
        if proxy_url is not None:
            client_options["proxy_url"] = proxy_url
        if proxy_ca_cert_file is not None:
            client_options["proxy_ca_certificate"] = proxy_ca_cert_file.read_text()

        store = S3Store(bucket=href_split.netloc, client_options=client_options, **s3_options)
        return store, href_split.path.lstrip("/")
    else:
        raise ValueError(f"Unknown scheme for href: {href}")
