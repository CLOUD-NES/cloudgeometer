from ..s3 import S3Config
from .async_geotiff import AsyncGeotiffReader
from .base import BaseReader
from .geopandas import GeopandasPyarrowReader
from .icechunk import IcechunkReader
from .kerchunk import KerchunkReader
from .rasterio import RasterioReader
from .rioxarray import RioxarrayReader

_REGISTRY: dict[str, type[BaseReader]] = {
    cls.NAME: cls
    for cls in (
        AsyncGeotiffReader,
        GeopandasPyarrowReader,
        IcechunkReader,
        KerchunkReader,
        RasterioReader,
        RioxarrayReader,
    )
}


def register(name: str, reader: type[BaseReader]):
    """Add a reader to the registry.

    Args:
        name (str): name of the reader, will be used as key in the reader
        reader (type[BaseReader]): reader class
    """
    _REGISTRY[name] = reader


def get_reader(
    name: str,
    proxy_url: str | None = None,
    proxy_ca_cert_file: str | None = None,
    s3_config: S3Config | None = None,
) -> BaseReader:
    """Get an instance of the reader.

    Args:
        name (str): name of the reader
        proxy_url (str | None): URL address of the proxy for request logging
        proxy_ca_cert_file (str | None): path to the proxy certificates
        s3_config (S3Config | None): configuration parameters for S3 access

    Raises:
        KeyError: if the registry does not contain a reader with the given name

    Returns:
        BaseReader: reader instance
    """
    if name not in _REGISTRY:
        raise KeyError(f"No reader registered for driver '{name}'")
    reader_cls = _REGISTRY[name]
    return reader_cls(
        proxy_url=proxy_url, proxy_ca_cert_file=proxy_ca_cert_file, s3_config=s3_config
    )


def list_readers() -> list[str]:
    """List the names of the readers in the registry.

    Returns:
        list[str]: reader names
    """
    return list(_REGISTRY.keys())
