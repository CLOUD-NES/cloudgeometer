from abc import ABC, abstractmethod
from typing import Any

import numpy as np


class BaseAccessor(ABC):
    def __init__(self, href: str, params: dict[str, Any] | None = None) -> None:
        self.href = href
        self.params = params or {}

    @abstractmethod
    def load(self, bbox: tuple[float, float, float, float] | None = None) -> np.ndarray:
        """Load the full dataset, or a subset within a bounding box.

        Args:
            bbox: Bounding box (left, bottom, right, top) in the dataset's
                own CRS. If None, the full dataset is read.
        """
        ...
