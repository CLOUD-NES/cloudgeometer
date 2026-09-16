# Cloudgeometer

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22802591.svg)](https://doi.org/10.5281/zenodo.22802591)
[![PyPI](https://img.shields.io/pypi/v/cloudgeometer.svg?colorB=blue)](https://pypi.python.org/project/cloudgeometer/)
[![License](https://img.shields.io/github/license/CLOUD-NES/cloudgeometer)](https://opensource.org/licenses/Apache-2.0)

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
