from .gdal import GDALBaseConverter


class VRTMosaicConverter(GDALBaseConverter):
    """Converter to produce a VRT mosaic based on GDAL CLI."""

    TEMPLATE = "gdal raster mosaic --output-format VRT {src} {dst} "