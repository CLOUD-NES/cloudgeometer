from ..s3 import S3Config
from .async_geotiff import AsyncGeotiffAccessor
from .base import BaseAccessor
from .geopandas import GeopandasPyarrowAccessor
from .icechunk import IcechunkAccessor
from .kerchunk import KerchunkAccessor
from .rasterio import RasterioAccessor
from .rioxarray import RioxarrayAccessor

_REGISTRY: dict[str, type[BaseAccessor]] = {
    cls.NAME: cls for cls in (
        AsyncGeotiffAccessor,
        GeopandasPyarrowAccessor,
        IcechunkAccessor,
        KerchunkAccessor,
        RasterioAccessor,
        RioxarrayAccessor,
    )
}


def register(name: str, accessor: type[BaseAccessor]):
    """Add a accessor to the registry.

    Args:
        name (str): name of the accessor, will be used as key in the accessor
        accessor (type[BaseAccessor]): accessor class
    """
    _REGISTRY[name] = accessor


def get_accessor(
    name: str,
    proxy_url: str | None = None,
    proxy_ca_cert_file: str | None = None,
    s3_config: S3Config | None = None
) -> BaseAccessor:
    """Get an instance of the accessor.

    Args:
        name (str): name of the accessor
        proxy_url (str | None): URL address of the proxy for request logging
        proxy_ca_cert_file (str | None): path to the proxy certificates
        s3_config (S3Config | None): configuration parameters for S3 access

    Raises:
        ValueError: if the registry does not contain an accessor with the given name

    Returns:
        BaseAccessor: accessor instance
    """
    if name not in _REGISTRY:
        raise KeyError(f"No accessor registered for driver '{name}'")
    accessor_cls = _REGISTRY[name]
    return accessor_cls(
        proxy_url=proxy_url, proxy_ca_cert_file=proxy_ca_cert_file, s3_config=s3_config
    )


def list_accessors() -> list[str]:
    """List the names of the accessors in the registry.

    Returns:
        list[str]: accessor names
    """
    return list(_REGISTRY.keys())
