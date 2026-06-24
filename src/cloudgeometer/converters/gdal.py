from typing import Any
from urllib.parse import urlsplit

from .base import BaseConverter, ConversionResult
from .shell import ShellMixin


class GDALMixin:
    """Mixin for converters that make use of GDAL."""

    def _to_vsi_uri(self, uri: str) -> str:
        """Normalize URI using GDAL virtual filesystem notation."""
        split = urlsplit(uri)
        if split.scheme == "s3":
            return "/".join(["/vsis3", split.netloc, split.path])
        elif split.scheme.startswith("http"):
            return "/".join(["/vsicurl", f"{split.scheme}:/", split.netloc, split.path])
        elif not split.scheme:
            return split.path
        else:
            return uri


class GDALBaseConverter(BaseConverter, ShellMixin, GDALMixin):
    """Base class for converters that make use of GDAL CLI.

    Derived classes can in principle only overwrite the `TEMPLATE` attribute using the "{src}" and "{dst}"
    templating strings for source and destination URIs.
    """

    TEMPLATE = "gdal --version"

    def run(self, src: str | list[str], dst: str) -> ConversionResult:

        if isinstance(src, str):
            src = [src]

        src = [self._to_vsi_uri(uri) for uri in src]
        dst = self._to_vsi_uri(dst)

        if len(src) == 1:
            src = src[0]

        return super().run(src=src, dst=dst)

    def _run(
        self,
        src: str | list[str],
        dst: str,
        params: dict[str, Any],
    ) -> ConversionResult:

        context = {
            "src": src if isinstance(src, str) else " ".join(src),
            "dst": dst,
            **params
        }

        rc, stdout, stderr = self.run_command(self.TEMPLATE, context)
        return self._shell_result(rc, stdout, stderr)
