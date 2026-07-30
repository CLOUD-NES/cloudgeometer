import numpy as np
import xarray

from .base import BaseAccessor


class KerchunkAccessor(BaseAccessor):
    """Data loader based on [xarray] and [kerchunk].

    [xarray]: https://docs.xarray.dev/
    [kerchunk]: https://fsspec.github.io/kerchunk/
    """

    def load(self, bbox: tuple[float, float, float, float] | None = None) -> np.ndarray:
        """Load the full dataset, or a subset within a bounding box."""
        ds = xarray.open_dataset(
            self.href,
            engine="kerchunk",
            storage_options={"remote_options": {"skip_instance_cache": True}},
        )
        da = ds["0"]  # TODO: fix hardcoded variable name
        if bbox:
            raise NotImplementedError()  # TODO: implement bbox filtering
        return da.values
