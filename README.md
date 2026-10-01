# Cloudgeometer <a href="https://github.com/CLOUD-NES/cloudgeometer"><img src="docs/logo/logo.png" align="right" height="250" alt="cloudgeometer logo" /></a>

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22802591.svg)](https://doi.org/10.5281/zenodo.22802591)
[![PyPI](https://img.shields.io/pypi/v/cloudgeometer.svg?colorB=blue)](https://pypi.python.org/project/cloudgeometer/)
[![License](https://img.shields.io/github/license/CLOUD-NES/cloudgeometer)](https://opensource.org/licenses/Apache-2.0)

> [!WARNING]
> This repository is work in progress, its content could change at any time.

Cloudgeometer is a tool to facilitate running data access geospatial benchmarks on cloud-native infrastructure.

## Installation

Cloudgeometer is distributed on [PyPI](https://pypi.org/), and can be installed with `pip`:

```shell
pip install cloudgeometer
```

## Examples

### Log HTTP requests with `RequestLogger`

Use `RequestLogger` as a context manager to log the HTTP requests sent while reading remote data.

For instance, loading a GeoTIFF with [rasterio](https://rasterio.readthedocs.io):

```python
import rasterio
from cloudgeometer import RequestLogger

href = "s3://example-bucket/path/to/image.tif"

with RequestLogger() as logger:
    with rasterio.Env(
        AWS_NO_SIGN_REQUEST="YES",
    ), rasterio.open(href) as dataset:
        data = dataset.read(1)

print(logger.logs)
# <5 requests, response size: 1.2 MB>

logs = logger.logs.to_df()
# request log table: method, url, status, bytes, range
```

### Run a benchmark with `Benchmark`

Wrap the same reading logic in a function, then pass it to `Benchmark` to time multiple runs:

```python
import rasterio
from cloudgeometer import Benchmark

def read_band(href, band=1):
    with rasterio.Env(
        AWS_NO_SIGN_REQUEST="YES"
    ), rasterio.open(href) as dataset:
        return dataset.read(band)

benchmark = Benchmark(
    href="s3://example-bucket/path/to/image.tif",
    reader=read_band,
    reader_params={"band": 1},
    num_runs=5,
)
results = benchmark.run()
print(results.summarize())
```

## Developing

Clone and access the GitHub repository:

```shell
git clone git@github.com:CLOUD-NES/cloudgeometer.git
cd cloudgeometer
```

We recommend to install cloudgeometer in a virtual environment, using either `pixi` or `uv` (but other virtual environment managers like Python `venv` and `conda` can be used as well).

### `pixi`

```shell
pixi install
# run tests
pixi run test
# run lint checks
pixi run lint
# run type checker
pixi run ty
```

### `uv`

```shell
uv sync --extra dev
# run tests
uv run pytest
# run lint checks
uv run ruff check && uv run ruff format --check
# run type checker
uv run ty check
```
