from .base import BaseConverter
from .base import ConversionResult
from .gdal import GDALMixin
from .shell import ShellMixin


class COGConverter(BaseConverter, ShellMixin, GDALMixin):
    """COG converter based on GDAL CLI.

    The conversion is carried out with `gdal raster translate` if a single
    source file is provided, while `gdal raster mosaic` is used for multiple
    source files.
    """

    TEMPLATE = (
        "gdal raster {cmd} "
        "--output-format COG "
        "--co BLOCKSIZE={blocksize} "
        "--co COMPRESS={compress} "
        "--overwrite "
        "{src} {dst} "
    )

    def _run(
        self,
        src: str | list[str],
        dst: str,
        blocksize: int = 512,
        compress: str = "LZW",
    ) -> ConversionResult:

        if isinstance(src, str):
            src = [src]

        src = [self._to_vsi_uri(uri) for uri in src]
        dst = self._to_vsi_uri(dst)
        cmd = "translate" if len(src) == 1 else "mosaic"

        context = {
            "cmd": cmd,
            "src": " ".join(src),
            "dst": dst,
            "blocksize": blocksize,
            "compress": compress,
        }

        rc, stdout, stderr = self.run_command(self.TEMPLATE, context)
        return self._shell_result(rc, stdout, stderr)
