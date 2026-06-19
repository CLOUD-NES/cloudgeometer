from .base import BaseConverter
from .cog import COGConverter

_REGISTRY: dict[str, type[BaseConverter]] = {
    "cog": COGConverter,
}


def register(name: str, driver: type[BaseConverter]):
    """Add a conversion driver to the registry.

    Args:
        name (str): name of the converter, will be used as key in the registry
        driver (type[BaseConverter]): converter class implementation
    """
    _REGISTRY[name] = driver


def get_converter(name: str) -> BaseConverter:
    """Set up a converter instance.

    Args:
        name (str): name of the converter

    Raises:
        ValueError: if the registry does not contain the specified key

    Returns:
        BaseConverter: converter instance
    """
    if name not in _REGISTRY:
        raise ValueError(f"No converter registered for driver '{name}'")
    return _REGISTRY[name]()
