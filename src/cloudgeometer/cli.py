import click

from .converters import get_converter
from .config import load_config
from .filesystem import expand_src_and_dst_uris
from .filesystem import file_exists
from .task import get_task_configs


@click.group()
def main() -> None:
    pass


@main.command()
@click.argument("config_file")
@click.option("--dry-run", is_flag=True, default=False)
def convert(config_file: str, dry_run: bool) -> None:
    configs = load_config(config_file)

    for config in configs:
        src = config.pop("src", None)
        dst = config.pop("dst", None)
        overwrite = config.pop("overwrite", True)

        srcs, dsts = expand_src_and_dst_uris(src, dst)
        tasks = get_task_configs(srcs=srcs, dsts=dsts, **config)

        if not overwrite:
            tasks = [task for task in tasks if not file_exists(task.dst)]

        for task in tasks:
            converter = get_converter(task.driver)
            print(converter)
            if not dry_run:
                res = converter.run(task.src, task.dst, **task.params)
                print(res)
