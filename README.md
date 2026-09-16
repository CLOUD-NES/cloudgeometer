# Cloudgeometer

> [!WARNING]
> This repository is work in progress, its content could change at any time.

Cloudgeometer is a tool to facilitate running data access geospatial benchmarks on cloud-native infrastructure.

## Developing

Clone and access the GitHub repository:

```shell
git clone git@github.com:CLOUD-NES/cloudgeometer.git
cd cloudgeometer
```

We recommend to install cloudgeometer in a virtual environment, using either `pixi` and `uv` (but other virtual environment managers like Python `venv` and `conda` can be used as well).

## `pixi`

```shell
pixi install
# run tests
pixi run test
# run lint checks
pixi run lint
# run type checker
pixi run ty
```

## `uv`

```shell
uv sync --extra dev
# run tests
uv run pytest
# run lint checks
uv run ruff check && uv run ruff format --check
# run type checker
uv run ty check
```
