import os
from typing import Any
from urllib.parse import urlsplit

import obstore
import rio_stac
import rustac
from obstore.store import LocalStore

from .base import BaseConverter, ConversionResult


class RioSTACConverter(BaseConverter):
    def _run(self, src: str | list[str], dst: str, params: dict[str, Any]) -> ConversionResult:

        srcs: list[str] = [src] if isinstance(src, str) else src

        _params: dict[str, Any] = params.copy()
        public_hrefs: bool = _params.pop("public_hrefs", False)

        items = [
            rio_stac.create_stac_item(
                source=source, asset_href=_public_href(source) if public_hrefs else None, **_params
            ).to_dict()
            for source in srcs
        ]

        dst_base, filename = os.path.split(dst)
        store = _get_store(dst_base)
        rustac.write_sync(href=filename, value=items, store=store)
        return ConversionResult(success=True)


def _get_store(uri: str) -> obstore.store.ObjectStore:
    """Set up a store for the given URI.

    If a protocol is missing, we assume a LocalStore.
    """
    protocol = urlsplit(uri).scheme
    store = obstore.store.from_url(uri) if protocol else LocalStore(prefix=uri, mkdir=True)
    return store


def _public_href(uri: str) -> str:
    """Build a public (HTTPS) URI.

    If it is already a HTTP(S) URI or a file path, return it as is.
    """
    parsed = urlsplit(uri)
    protocol = parsed.scheme
    if protocol == "s3":
        bucket = parsed.netloc
        key = parsed.path.lstrip("/")
        endpoint_url = os.getenv("AWS_ENDPOINT_URL", "").rstrip("/")
        if endpoint_url:
            return f"{endpoint_url}/{bucket}/{key}"
        return f"https://{bucket}.s3.amazonaws.com/{key}"
    elif protocol.startswith("http") or not protocol:
        # if the URL is already public or we have a local path, leave it as is
        return uri
    else:
        raise ValueError(f"Unsupported URI scheme: {protocol!r}")
