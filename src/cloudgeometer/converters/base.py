import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ConversionProfile:
    id: str
    driver: str
    params: dict[str, Any]


@dataclass
class ConversionResult:
    success: bool
    time: float | None = None
    stdout: str | None = None
    stderr: str | None = None
    error: str | None = None


class BaseConverter(ABC):
    """Base class for the converters.

    All converters share the same logic for timing and result wrapping.
    """
    def __init__(self, params: dict[str, Any]) -> None:
        self.params = params

    @abstractmethod
    def _run(self, src: str | list[str], dst: str, params: dict[str, Any]) -> ConversionResult: ...

    def run(self, src: str | list[str], dst: str) -> ConversionResult:
        """Run the conversion.

        Returns:
            ConversionResult: report on the outcome of the run.
        """
        t0 = time.perf_counter()
        try:
            result = self._run(src, dst, self.params)
            result.time = time.perf_counter() - t0
            return result
        except Exception as e:
            return ConversionResult(
                success=False,
                time=time.perf_counter() - t0,
                error=str(e),
            )
