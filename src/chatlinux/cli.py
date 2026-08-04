"""CLI entrypoint for chatlinux."""

import click

from chatlinux import __version__


@click.group()
@click.version_option(__version__, prog_name="chatlinux")
def main() -> None:
    """chatlinux command line interface."""
    # Add package-specific commands here. Prefer ChatStyle helpers for
    # interactive input when a command needs recoverable user input.


if __name__ == "__main__":
    main()
