from typing import Any

from .base import ConversionResult
from .gdal import GDALBaseConverter


class COGConverter(GDALBaseConverter):
    """COG converter based on GDAL CLI."""

    TEMPLATE = (
        "gdal raster translate "
        "--output-format COG "
        "--co BLOCKSIZE={blocksize} "
        "--co COMPRESS={compress} "
        "--co BIGTIFF={bigtiff} "
        "--overwrite "
        "{src} {dst} "
    )

    def __init__(self, blocksize: int = 512, compress: str = "LZW", bigtiff: str = "NO") -> None:
        self.params = {
            "blocksize": blocksize,
            "compress": compress,
            "bigtiff": bigtiff,
        }

    def _run(self, src: str | list[str], dst: str, params: dict[str, Any]) -> ConversionResult:
        if not isinstance(src, str):
            raise ValueError(f"GDAL translate only accepts one source, got: {src}")
        return super()._run(src=src, dst=dst, params=params)


class COGMosaicConverter(GDALBaseConverter):
    """Converter to produce a COG mosaic based on GDAL CLI."""

    TEMPLATE = (
        "gdal raster mosaic "
        "--output-format COG "
        "--co BLOCKSIZE={blocksize} "
        "--co COMPRESS={compress} "
        "--co BIGTIFF={bigtiff} "
        "--overwrite "
        "{src} {dst} "
    )

    def __init__(self, blocksize: int = 512, compress: str = "LZW", bigtiff: str = "NO") -> None:
        self.params = {
            "blocksize": blocksize,
            "compress": compress,
            "bigtiff": bigtiff,
        }



class COGTileConverter(GDALBaseConverter):
    """Converter to form retile GDAL CLI."""

    TEMPLATE = (
        "gdal raster pipeline "
        "  ! mosaic {src} "
        "  ! tile "
        "    --tiling-scheme=raster "
        "    --tile-size={tile_size}"
        "    --output-format=COG "
        "    --co BLOCKSIZE={blocksize} "
        "    --co COMPRESS={compress} "
        "    --co BIGTIFF={bigtiff} "
        "    --overwrite "
        "    {dst} "
    )

    def __init__(self, tile_size: int, blocksize: int = 512, compress: str = "LZW", bigtiff: str = "NO") -> None:
        self.params = {
            "tile_size": tile_size,
            "blocksize": blocksize,
            "compress": compress,
            "bigtiff": bigtiff,
        }