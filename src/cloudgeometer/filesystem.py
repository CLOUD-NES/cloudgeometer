from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import fsspec


def expand_src_and_dst_uris(src: str, dst: str) -> tuple[list[str], list[str]]:
    """Expand source and destination URIs.

    Wildcards are expanded and destination paths completed with filenames whenever these were
    not given in input.

    Args:
        src (str): source URI
        dst (str): destination URI

    Returns:
        tuple[list[str], list[str]]: expanded source and destination URIs.
    """
    # resolve wildcards and extract source paths from src
    srcs = _resolve_uri(src)

    # if the destination path looks like a directory, append the source filename(s)
    src_paths = [_get_path(src) for src in srcs]
    dst_path = _get_path(dst)
    if _looks_like_dir(dst_path):
        src_filenames = [src.name for src in src_paths]
        dst_paths = [dst_path / src_filename for src_filename in src_filenames]
    else:
        dst_paths = [dst_path]
    dsts = [_replace_path(dst, path) for path in dst_paths]
    assert len(srcs) >= 1 and len(dsts) >= 1

    return srcs, dsts


def file_exists(uri: str):
    """Check if local or remote file exists.

    Args:
        uri (str): file URI

    Returns:
        bool: True if file exists
    """
    uri_split = urlsplit(uri)
    fs = fsspec.filesystem(uri_split.scheme)
    return fs.exists(uri)


def _replace_path(uri: str, path: str | Path) -> str:
    return urlunsplit(urlsplit(uri)._replace(path=str(path)))


def _resolve_uri(uri: str) -> list[str]:
    uri_split = urlsplit(uri)
    fs = fsspec.filesystem(uri_split.scheme)
    paths = fs.glob(uri)
    # for s3 URIs, the path returned by glob includes the bucket name
    paths = [path.removeprefix(uri_split.netloc) for path in paths]
    return [_replace_path(uri, path) for path in paths]


def _get_path(uri: str) -> Path:
    return Path(urlsplit(uri).path)


def _looks_like_dir(path: Path) -> bool:
    """Looks like a directory path."""
    return not path.suffix
