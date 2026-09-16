from typing import Any

import numpy as np
import rioxarray

from .base import BaseReader
from .rasterio import rasterio_env


class RioxarrayReader(BaseReader):
    """Data reader based on [rioxarray][rioxarray].

    [rioxarray]: https://corteva.github.io/rioxarray
    """

    NAME: str = "rioxarray"
    PARAMS: tuple = ("bbox",)

    def _read(self, href: str, params: dict[str, Any]) -> np.ndarray:
        """Load the full dataset, or a subset within a bounding box."""
        bbox = params.get("bbox")
        # need to use as a context manager to avoid rasterio>=1.5 error: https://github.com/rasterio/rasterio/issues/3563
        with (
            rasterio_env(self.proxy_url, self.proxy_ca_cert_file, self.s3_config),
            rioxarray.open_rasterio(href, cache=False) as da,  # type: ignore
        ):
            if bbox is not None:
                da = da.rio.clip_box(*bbox)
            return np.asanyarray(da.values)
