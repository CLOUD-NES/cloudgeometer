# Cloud Geometer

> [!WARNING]
> This repository is work in progress, its content could change at any time.

Setup and run benchmarks for cloud-native with geospatial datasets.

## Setup

Dependencies are managed with [pixi](https://pixi.sh). To install and activate the environment:

```bash
pixi install
pixi shell
```

## Usage

```bash
cloudgeometer convert ./config/ahn-dsm05.yml
```

## Development

Linting and tests can be run as:

```bash
pixi run lint
pixi run test
```