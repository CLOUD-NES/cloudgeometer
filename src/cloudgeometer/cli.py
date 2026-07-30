import logging

import click
import dotenv

from .accessors import guess_accessors, list_accessors
from .benchmark import Benchmark
from .config import parse_config_file
from .tracker import DEFAULT_PROXY_PORT

logger = logging.getLogger(__name__)


@click.group()
@click.version_option()
@click.option(
    "--env-file",
    type=click.Path(exists=True, dir_okay=False),
    help="File where to load environment variables from.",
)
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="Print debug logs.",
)
def main(env_file: str | None = None, debug: bool = False) -> None:
    """Set up and run data access benchmarks."""
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    dotenv.load_dotenv(dotenv_path=env_file, override=False, verbose=debug)


@main.command()
def configure() -> None:
    """Generate benchmark configurations."""
    raise NotImplementedError("Functionality to generate configuration files is still missing.")


@main.command()
@click.option(
    "--config-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to the benchmark configuration file.",
)
@click.option("--href", type=str, help="URL to the dataset file or directory.")
@click.option(
    "--accessor",
    type=click.Choice(list_accessors(), case_sensitive=False),
    help="Accessor(s) used for benchmarking.",
    multiple=True,
)
@click.option(
    "--network-stats",
    is_flag=True,
    default=False,
    help="Measure network-related metrics.",
)
@click.option(
    "--proxy-port",
    type=int,
    default=DEFAULT_PROXY_PORT,
    help="Port which the proxy for network monitoring will listen to.",
)
def run(
    config_file: str | None,
    href: str | None,
    accessor: tuple | None,
    network_stats: bool = False,
    proxy_port: int | None = None,
) -> None:
    """Run one or more benchmarks.

    Execute the benchmark(s) defined either via the CLI arguments or via a configuration file.
    """
    if config_file and (href or accessor or network_stats):
        logger.warning("A configuration file is provided, other CLI arguments will be neglected")

    if config_file is not None:
        configs = parse_config_file(config_file)
        benchmarks = [Benchmark(**config) for config in configs]
    elif href is not None:
        accessors = accessor or guess_accessors(href)
        benchmarks = [
            Benchmark(
                id=accessor,
                href=href,
                accessor=accessor,
                network_stats=network_stats,
                proxy_port=proxy_port,
            )
            for accessor in accessors
        ]
    else:
        raise ValueError("Provide a configuration file or a dataset URL.")

    for benchmark in benchmarks:
        benchmark.run()
        benchmark.summary()
