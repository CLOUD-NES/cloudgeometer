from urllib.parse import urlsplit


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
