import numpy as np
import rioxarray

from .base import BaseAccessor


class RioxarrayAccessor(BaseAccessor):
    """Data loader based on [rioxarray][rioxarray].

    [rioxarray]: https://corteva.github.io/rioxarray
    """

    def load(self, bbox: tuple[float, float, float, float] | None = None) -> np.ndarray:
        """Load the full dataset, or a subset within a bounding box."""
        # need to use as a context manager to avoid rasterio>=1.5 error: https://github.com/rasterio/rasterio/issues/3563
        with rioxarray.open_rasterio(self.href, **self.params) as da:  # type: ignore
            if bbox:
                da = da.rio.clip_box(*bbox)
            return np.asanyarray(da.values)
