import logging

import click

from ..readers import list_readers
from ..request_logger.proxy import DEFAULT_PROXY_PORT
from ..s3 import S3Config
from .run import run_reader_benchmark


@click.group()
@click.version_option()
@click.option("--endpoint-url")
@click.option("--region")
@click.option("--access-key-id")
@click.option("--secret-access-key")
@click.option("--debug", is_flag=True, default=False, help="Print debug logs.")
@click.pass_context
def cli(
    ctx,
    endpoint_url: str | None,
    region: str | None,
    access_key_id: str | None,
    secret_access_key: str | None,
    debug: bool = False,
) -> None:
    """Set up and run data access benchmarks."""
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    ctx.obj = S3Config.from_env(
        endpoint_url=endpoint_url,
        region=region,
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
    )


@cli.command()
@click.argument("href", type=str)
@click.option(
    "--reader",
    type=click.Choice(list_readers(), case_sensitive=False),
    help="Reader(s) used for the benchmark.",
)
@click.option(
    "--num-runs",
    type=int,
    default=1,
    help="Number of times the task is repeated to accumulate statistics."
)
@click.option(
    "--log-requests",
    is_flag=True,
    default=False,
    help="Keep logs of the requests via a proxy.",
)
@click.option(
    "--proxy-port",
    type=int,
    default=DEFAULT_PROXY_PORT,
    help="Port which the proxy to log requests will listen to.",
)
@click.option(
    "--json",
    is_flag=True,
    default=False,
    help="Write output as JSON."
)
@click.pass_obj
def run(
    s3_config: S3Config,
    href: str,
    reader: str,
    num_runs: int,
    log_requests: bool,
    proxy_port: int,
    json: bool,
):
    """Run a benchmark using one of the implemented readers.

    Provide the URL/path to the local or remote dataset, select a reader, and, optionally, one or
    more configuration parameters.
    """
    result = run_reader_benchmark(
        href=href,
        reader=reader,
        bbox=None,
        band=None,
        columns=None,
        group=None,
        log_requests=log_requests,
        num_runs=num_runs,
        proxy_port=proxy_port,
        s3_config=s3_config,
    )
    if not json:
        click.echo(result.summary())
    else:
        click.echo(result.as_json())
