import numpy as np
import rasterio
from rasterio.windows import from_bounds

from .base import BaseAccessor


class RasterioAccessor(BaseAccessor):
    """Data loader based on [rasterio].

    [rasterio]: https://rasterio.readthedocs.io
    """

    def load(self, bbox: tuple[float, float, float, float] | None = None) -> np.ndarray:
        """Load the full dataset, or a subset within a bounding box."""
        with rasterio.open(self.href, **self.params) as dataset:
            if not bbox:
                return dataset.read()
            else:
                window = from_bounds(*bbox, transform=dataset.transform)
                return dataset.read(window=window)
