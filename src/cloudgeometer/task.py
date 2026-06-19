from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TaskConfig:
    id: str
    driver: str
    src: str | list[str]
    dst: str
    params: dict[str, Any]


def get_task_configs(
    id: str,
    srcs: list[str],
    dsts: list[str],
    driver: str,
    params: dict[str, Any] | None = None,
) -> list[TaskConfig]:

    tasks = []

    if len(srcs) == len(dsts):
        for src, dst in zip(srcs, dsts, strict=True):
            tasks.append(TaskConfig(id=id, driver=driver, src=src, dst=dst, params=params or {}))
    elif len(dsts) == 1:
        tasks.append(TaskConfig(id=id, driver=driver, src=srcs, dst=dsts[0], params=params or {}))
    else:
        raise ValueError("Conversions allowed are (n -> n) or (n -> 1) files.")

    return tasks

