from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import obstore
import rio_stac
import rustac

from .base import BaseConverter, ConversionResult


class RioSTACConverter(BaseConverter):
    def _run(self, src: str | list[str], dst: str, params: dict[str, Any]) -> ConversionResult:
        src = [src] if isinstance(src, str) else src
        items = [rio_stac.create_stac_item(tile_path, **params).to_dict() for tile_path in src]
        url, path = _split_base_url(dst)
        store = obstore.store.from_url(url)
        rustac.write_sync(href=path, value=items, store=store)
        return ConversionResult(success=True)


def _split_base_url(uri: str):
    """Split an URI/path into a base URI and path.

    Examples:
        >>> _split_base_url("s3://mybucket/path/to/file.txt")
        ('s3://mybucket', '/path/to/file.txt')
        >>> _split_base_url("/path/to/file.txt")
        ('file:///path/to', 'file.txt')
    """
    uri_split = urlsplit(uri)
    # if we have
    if uri_split.scheme:
        url = urlunsplit(uri_split._replace(path=""))
        path = uri_split.path
    else:
        p = Path(uri).resolve()
        url = p.parent.as_uri()
        path = p.name
    return url, path
