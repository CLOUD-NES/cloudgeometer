from typing import Any

from .base import ConversionResult
from .gdal import GDALBaseConverter


class GeoTIFFConverter(GDALBaseConverter):
    """COG converter based on GDAL CLI."""

    TEMPLATE = (
        "gdal raster translate "
        "--output-format GTiff "
        "--co TILED=YES "
        "--co BLOCKXSIZE={blocksize} "
        "--co BLOCKYSIZE={blocksize} "
        "--co COMPRESS={compress} "
        "--overwrite "
        "{src} {dst} "
    )

    def _run(self, src: str | list[str], dst: str, params: dict[str, Any]) -> ConversionResult:
        if not isinstance(src, str):
            raise ValueError(f"GDAL translate only accepts one source, got: {src}")
        return super()._run(src=src, dst=dst, params=params)
