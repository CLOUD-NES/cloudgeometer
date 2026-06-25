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

Set the following environment variables for authenticating to the S3 store:

```shell
# required by s3fs, obstore, rustac
export AWS_ACCESS_KEY_ID="<YOUR-ACCESS-KEY-ID>"
export AWS_SECRET_ACCESS_KEY="<YOUR-SECRET-ACCESS-KEY>"
export AWS_ENDPOINT_URL="https://objectstore.surf.nl"
# required by GDAL
export AWS_S3_ENDPOINT="objectstore.surf.nl"
export CPL_VSIL_USE_TEMP_FILE_FOR_RANDOM_WRITE="YES"
```

Run all the conversions defined in the YAML config file:

```bash
cloudgeometer convert ./config/ahn-dsm05.yml
```

## Development

Linting and tests can be run as:

```bash
pixi run lint
pixi run test
```