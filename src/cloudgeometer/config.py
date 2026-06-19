import copy
import itertools
import re
from typing import Any

import yaml

MATRIX_RE = re.compile(r"\$\{\{\s*matrix\.([a-zA-Z0-9_]+)\s*\}\}")


def _substitute(value, matrix_values):
    """Recursively substitute matrix variables."""
    if isinstance(value, str):
        matches = MATRIX_RE.findall(value)

        # If the entire string is a single matrix reference,
        # return the native type (int, bool, etc.)
        if len(matches) == 1 and MATRIX_RE.fullmatch(value):
            return matrix_values[matches[0]]

        # Otherwise substitute as strings
        def repl(match):
            key = match.group(1)
            return str(matrix_values[key])

        return MATRIX_RE.sub(repl, value)

    if isinstance(value, dict):
        return {k: _substitute(v, matrix_values) for k, v in value.items()}

    if isinstance(value, list):
        return [_substitute(v, matrix_values) for v in value]

    return value


def _expand_matrix(id: str, config: dict[str, Any]) -> list[dict[str, Any]]:

    config = copy.deepcopy(config)
    matrix = config.pop("matrix", None)

    if matrix is None:
        config["id"] = id
        return [config]

    jobs = []

    for n, combination in enumerate(itertools.product(*matrix.values())):
        expanded = copy.deepcopy(config)
        matrix_values = dict(zip(matrix.keys(), combination, strict=True))
        expanded = _substitute(expanded, matrix_values)
        expanded["id"] = f"{id}-{n}"
        jobs.append(expanded)

    return jobs


def load_config(path: str) -> list[dict[str, Any]]:
    """Load and expand job config file.

    Args:
        path (str): path to the yaml file.

    Returns:
        list[dict[str, Any]]: list of job configurations.
    """
    with open(path) as f:
        data = yaml.safe_load(f)
    jobs = []
    for name, config in data["jobs"].items():
        jobs.extend(_expand_matrix(name, config))
    return jobs
