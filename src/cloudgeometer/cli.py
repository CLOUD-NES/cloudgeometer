from collections.abc import Iterator
import click

from .config import load_config
from .converters import get_converter
from .filesystem import expand_src_and_dst_uris, file_exists


@click.group()
def main() -> None:  # noqa: D103
    pass


@main.command()
@click.argument("config_file")
@click.option("--dry-run", is_flag=True, default=False)
def convert(config_file: str, dry_run: bool) -> None:
    """Run a sequence of conversion tasks.

    Args:
        config_file (str): path to the YAML configuration file
        dry_run (bool): only check source/destinations without running the conversions
    """
    configs = load_config(config_file)

    for config in configs:
        src = config.get("src", "")
        dst = config.get("dst", "")
        overwrite = config.get("overwrite", True)
        driver = config.get("driver", "")
        params = config.get("params", {})

        srcs, dsts = expand_src_and_dst_uris(src, dst)
        converter = get_converter(driver, params)

        for src, dst in zip(srcs, dsts, strict=True):

            if not overwrite and file_exists(dst):
                continue

            if not dry_run:
                res = converter.run(src, dst)
                print(res)
