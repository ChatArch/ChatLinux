"""CLI entrypoint for chatlinux."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import click
from chatstyle import add_tree_option

from chatlinux import __version__
from chatlinux.fleet import FleetError, format_table, init_config, load_cache, refresh_track, state_paths


@click.group(name="chatlinux")
@click.version_option(__version__, prog_name="chatlinux")
@add_tree_option(renderer_options={"root_name": "chatlinux"})
def main() -> None:
    """chatlinux command line interface."""
    # Prefer ChatStyle helpers for interactive input when a command needs
    # recoverable user input. Fleet MVP commands are non-interactive and
    # shell-friendly by design.


@main.group("fleet")
@click.option(
    "--home",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="ChatLinux state directory. Defaults to $CHATLINUX_HOME, then $CHATARCH_HOME/chatlinux, then ~/.chatarch/chatlinux.",
)
@click.pass_context
def fleet_group(ctx: click.Context, home: Path | None) -> None:
    """Track server fleets and view cached health status."""

    ctx.obj = {"home": home}


@fleet_group.command("init")
@click.option("--sample", default="cube", show_default=True, help="Sample track config to write.")
@click.option("--force", is_flag=True, help="Overwrite an existing fleet config.")
@click.option("--json", "json_output", is_flag=True, help="Print machine-readable JSON.")
@click.pass_context
def fleet_init(ctx: click.Context, sample: str, force: bool, json_output: bool) -> None:
    """Initialize a fleet config under the ChatLinux state directory."""

    home = _home(ctx)
    try:
        config = init_config(home, sample=sample, force=force)
    except FleetError as exc:
        raise click.ClickException(str(exc)) from exc
    paths = state_paths(home)
    payload: dict[str, Any] = {
        "home": str(home),
        "config_path": str(paths["config"]),
        "state_paths": {name: str(path) for name, path in paths.items()},
        "default_track": config.get("default_track"),
        "tracks": sorted((config.get("tracks") or {}).keys()),
    }
    _emit(payload, json_output=json_output, table=f"Wrote fleet config: {payload['config_path']}\n")


@fleet_group.command("refresh")
@click.option("--track", default="cube", show_default=True, help="Fleet track to refresh.")
@click.option("--json", "json_output", is_flag=True, help="Print machine-readable JSON.")
@click.pass_context
def fleet_refresh(ctx: click.Context, track: str, json_output: bool) -> None:
    """Run Ansible read-only checks and update the local cache."""

    home = _home(ctx)
    try:
        snapshot = refresh_track(home, track=track)
    except FleetError as exc:
        raise click.ClickException(str(exc)) from exc
    _emit(snapshot, json_output=json_output, table=format_table(snapshot))


@fleet_group.command("show")
@click.option("--track", default="cube", show_default=True, help="Fleet track to read from cache.")
@click.option("--json", "json_output", is_flag=True, help="Print machine-readable JSON.")
@click.pass_context
def fleet_show(ctx: click.Context, track: str, json_output: bool) -> None:
    """Show the last cached fleet status without contacting hosts."""

    home = _home(ctx)
    try:
        snapshot = load_cache(home, track=track)
    except FleetError as exc:
        raise click.ClickException(str(exc)) from exc
    _emit(snapshot, json_output=json_output, table=format_table(snapshot))


@fleet_group.command("status")
@click.option("--track", default="cube", show_default=True, help="Fleet track to show.")
@click.option("--refresh", is_flag=True, help="Refresh with Ansible before showing status.")
@click.option("--json", "json_output", is_flag=True, help="Print machine-readable JSON.")
@click.pass_context
def fleet_status(ctx: click.Context, track: str, refresh: bool, json_output: bool) -> None:
    """Show cached fleet status, optionally refreshing first."""

    home = _home(ctx)
    try:
        snapshot = refresh_track(home, track=track) if refresh else load_cache(home, track=track)
    except FleetError as exc:
        raise click.ClickException(str(exc)) from exc
    _emit(snapshot, json_output=json_output, table=format_table(snapshot))


def _home(ctx: click.Context) -> Path:
    home = (ctx.obj or {}).get("home")
    if home is None:
        from chatlinux.fleet import default_home

        return default_home()
    return home


def _emit(payload: MappingLike, *, json_output: bool, table: str) -> None:
    if json_output:
        click.echo(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        click.echo(table, nl=False)


MappingLike = dict[str, Any]


if __name__ == "__main__":
    main()
