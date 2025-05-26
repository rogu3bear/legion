import subprocess

import click


@click.command()
@click.option(
    "--dev-start",
    is_flag=True,
    help="Start the local development environment.",
)
def dev_start(dev_start):
    """Start the local development environment."""
    if dev_start:
        subprocess.run(["./scripts/dev_start.sh"], check=True)
