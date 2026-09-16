from typing import Any
from urllib.parse import urlsplit

import icechunk
import xarray

from ..s3 import S3Config
from .base import BaseReader


class IcechunkReader(BaseReader):
    """Data reader based on [xarray] and [icechunk].

    [xarray]: https://docs.xarray.dev/
    [icechunk]: https://icechunk.io
    """

    NAME = "icechunk"

    def _read(self, href: str, params: dict[str, Any]) -> Any:
        """Load the full dataset, or a subset within a bounding box."""
        repo = _open_repository(href, self.s3_config)
        session = repo.readonly_session("main")
        ds = xarray.open_zarr(session.store, consolidated=False, zarr_format=3)
        da = ds["0"]  # TODO: fix hardcoded variable name
        return da.values


def _open_repository(uri: str, s3_config: S3Config) -> icechunk.Repository:
    uri_split = urlsplit(uri)
    if uri_split.scheme == "s3":
        bucket = uri_split.netloc
        prefix = uri_split.path.lstrip("/")
        # anonymous access to the icechunk repository requires public s3 listing
        storage = icechunk.s3_storage(
            bucket=bucket,
            prefix=prefix,
            region=s3_config.region,
            endpoint_url=s3_config.endpoint_url,
            access_key_id=s3_config.access_key_id,
            secret_access_key=s3_config.secret_access_key,
            anonymous=s3_config.is_anonymous,
        )
        credentials = icechunk.containers_credentials(
            {
                f"s3://{bucket}/": icechunk.s3_credentials(
                    access_key_id=s3_config.access_key_id,
                    secret_access_key=s3_config.secret_access_key,
                    anonymous=s3_config.is_anonymous,
                )
            }
        )
    else:
        raise NotImplementedError()
    return icechunk.Repository.open(
        storage=storage,
        authorize_virtual_chunk_access=credentials,
    )
