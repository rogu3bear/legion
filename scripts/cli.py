import subprocess

import click


@click.command()
@click.option(
    "--dev-start",
    is_flag=True,
    help="Start the development environment using Docker Compose.",
)
def dev_start(dev_start):
    """Start the development environment using Docker Compose."""
    if dev_start:
        subprocess.run(["./scripts/dev_start.sh"], check=True)
