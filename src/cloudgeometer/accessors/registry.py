from typing import Any

from .base import BaseAccessor
from .icechunk import IcechunkAccessor
from .kerchunk import KerchunkAccessor
from .rasterio import RasterioAccessor
from .rioxarray import RioxarrayAccessor

_REGISTRY: dict[str, type[BaseAccessor]] = {
    "kerchunk": KerchunkAccessor,
    "icechunk": IcechunkAccessor,
    "rasterio": RasterioAccessor,
    "rioxarray": RioxarrayAccessor,
}


def register(name: str, accessor: type[BaseAccessor]):
    """Add an accessor to the registry.

    Args:
        name (str): name of the accessor, will be used as key in the accessor
        accessor (type[BaseAccessor]): accessor class
    """
    _REGISTRY[name] = accessor


def get_accessor(name: str, href: str, params: dict[str, Any] | None = None) -> BaseAccessor:
    """Get an instance of the accessor.

    Args:
        name (str): name of the accessor
        href (str): URL to the dataset file or directory.
        params (dict[str, Any] | None): optional parameters to configure the accessor.

    Raises:
        ValueError: if the registry does not contain an accessor with the given name

    Returns:
        type[BaseAccessor]: accessor instance
    """
    if name not in _REGISTRY:
        raise KeyError(f"No accessor registered for driver '{name}'")
    return _REGISTRY[name](href=href, params=params or {})


def list_accessors() -> list[str]:
    """List the names of the accessors in the registry.

    Returns:
        list[str]: accessor names
    """
    return list(_REGISTRY.keys())
