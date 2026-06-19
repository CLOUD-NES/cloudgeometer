from .base import BaseConverter
from .cog import COGConverter

_REGISTRY: dict[str, type[BaseConverter]] = {
    "cog": COGConverter,
}


def register(name: str, driver: type[BaseConverter]):
    _REGISTRY[name] = driver


def get_converter(name: str) -> BaseConverter:
    if name not in _REGISTRY:
        raise ValueError(f"No converter registered for driver '{name}'")
    return _REGISTRY[name]()
