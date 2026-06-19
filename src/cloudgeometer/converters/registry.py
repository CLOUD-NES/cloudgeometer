from .base import BaseConverter
from .cog import COGConverter, COGMosaicConverter
from .vrt import VRTMosaicConverter

_REGISTRY: dict[str, type[BaseConverter]] = {
    "cog": COGConverter,
    "cog-mosaic": COGMosaicConverter,
    "vrt": VRTMosaicConverter,
}


def register(name: str, driver: type[BaseConverter]):
    """Add a converter to the registry.

    Args:
        name (str): name of the converter, will be used as key in the registry
        driver (type[BaseConverter]): converter class
    """
    _REGISTRY[name] = driver


def get_converter(name: str) -> BaseConverter:
    """Set up a converter instance.

    Args:
        name (str): name of the converter

    Raises:
        ValueError: if the registry does not contain a converter with the given name

    Returns:
        BaseConverter: converter instance
    """
    if name not in _REGISTRY:
        raise ValueError(f"No converter registered for driver '{name}'")
    return _REGISTRY[name]()


def list_converters() -> list[str]:
    """List the names of the converters in the registry.

    Returns:
        list[str]: converter names
    """
    return list(_REGISTRY.keys())
