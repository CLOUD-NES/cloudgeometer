# Setting up initial datasets

## Configuration

Setup the following environmental variables to configure access to the store:

```bash
# for aws-cli, s3fs, obstore, rustac
export AWS_ACCESS_KEY_ID="<YOUR-ACCESS-KEY-ID>"
export AWS_SECRET_ACCESS_KEY="<YOUR-SECRET-ACCESS-KEY>"
export AWS_ENDPOINT_URL="https://objectstore.surf.nl"
# in addition, for GDAL
export AWS_S3_ENDPOINT="objectstore.surf.nl"
```

## Datasets

### Actueel Hoogtebestand Nederland (AHN) - Point cloud and DSM 50 cm

Download Point Cloud data (COPC) and the derived raster Digital Surface Model at 0.5 m resolution (GeoTIFF) using [ahn-cli](https://github.com/CLOUD-NES/ahn-stac/tree/main/tools/ahn-cli):

```shell
ahn download \
    --ahn-version 4 \
    --bbox 5.085297 52.050390 5.197220 52.117516 \
    --destination s3://cloud-nes-benchmarks/ahn/4/raw \
    --asset-key DSM05 \
    --asset-key PC \
    --output s3://cloud-nes-benchmarks/ahn/4/raw/items.parquet
```
