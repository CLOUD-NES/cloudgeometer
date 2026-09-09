import dataclasses

import pandas

from ..utils import as_human_readable_size


@dataclasses.dataclass(frozen=True)
class RequestLog:
    """A logged HTTP request/response."""

    method: str
    url: str
    status: int
    bytes: int
    range: str | None


class RequestLogCollection:
    """A collection of request logs."""

    def __init__(self):
        self._request_logs: list[RequestLog] = []

    def extend(self, request_logs: list[RequestLog]) -> None:
        """Extend the collection with the given request logs.

        Args:
            request_logs (list[RequestLog]): logged requests.
        """
        self._request_logs.extend(request_logs)

    @property
    def total_bytes(self) -> int:
        """Size of response across the collection.

        Returns:
            int: total response bytes
        """
        return sum(r.bytes for r in self._request_logs)

    def to_df(self) -> pandas.DataFrame:
        """Return the collection as a pandas DataFrame.

        Returns:
            DataFrame: table of logged requests
        """
        return pandas.DataFrame([dataclasses.asdict(log) for log in self._request_logs])

    def __len__(self) -> int:
        return len(self._request_logs)

    def __repr__(self) -> str:
        size = as_human_readable_size(self.total_bytes)
        return f"<{len(self)} requests, {size} response size>"
