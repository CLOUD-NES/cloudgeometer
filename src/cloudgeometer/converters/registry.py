from typing import Type
from .base import BaseConverter
from .cog import COGConverter

_REGISTRY: dict[str, Type[BaseConverter]] = {
    "cog": COGConverter,
}


def register(name: str, driver: Type[BaseConverter]):
    _REGISTRY[name] = driver


def get_converter(name: str) -> BaseConverter:
    if name not in _REGISTRY:
        raise ValueError(f"No converter registered for driver '{name}'")
    return _REGISTRY[name]()
