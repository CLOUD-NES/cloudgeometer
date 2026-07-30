from urllib.parse import urlsplit

import icechunk
import numpy as np
import xarray

from .base import BaseAccessor


class IcechunkAccessor(BaseAccessor):
    """Data loader based on [xarray] and [icechunk].

    [xarray]: https://docs.xarray.dev/
    [icechunk]: https://icechunk.io
    """

    def load(self, bbox: tuple[float, float, float, float] | None = None) -> np.ndarray:
        """Load the full dataset, or a subset within a bounding box."""
        repo = _open_repository(self.href)
        session = repo.readonly_session("main")
        ds = xarray.open_zarr(session.store, consolidated=False, zarr_format=3)
        da = ds["0"]  # TODO: fix hardcoded variable name
        if bbox:
            raise NotImplementedError()  # TODO: implement bbox filtering
        return da.values


def _open_repository(uri):
    uri_split = urlsplit(uri)
    if uri_split.scheme == "s3":
        bucket = uri_split.netloc
        prefix = uri_split.path.lstrip("/")
        storage = icechunk.s3_storage(
            bucket=bucket,
            prefix=prefix,
            from_env=True,
        )
        credentials = icechunk.containers_credentials(
            {f"s3://{bucket}/": icechunk.s3_credentials(from_env=True)}
        )
    else:
        raise NotImplementedError()
    return icechunk.Repository.open(
        storage=storage,
        authorize_virtual_chunk_access=credentials,
    )
