"""CLI entrypoint for chatlinux."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import click

from chatlinux import __version__
from chatlinux.fleet import FleetError, format_table, init_config, load_cache, refresh_track, state_paths


def _format_metavar(name: str) -> str:
    return name.replace("_", "-").upper()


def _format_argument(param: click.Argument) -> str:
    metavar = _format_metavar(param.name)
    return metavar if param.required else f"[{metavar}]"


def _format_option(param: click.Option) -> str:
    preferred = next((opt for opt in param.opts if opt.startswith("--")), param.opts[0])
    if param.is_flag or param.flag_value is not None:
        return preferred
    metavar = param.metavar or _format_metavar(param.name)
    return f"{preferred} {metavar}" if param.required else f"[{preferred} {metavar}]"


def _command_signature(command: click.Command) -> str:
    parts: list[str] = []
    for param in command.params:
        if isinstance(command, click.Group) and isinstance(param, click.Option):
            continue
        if isinstance(param, click.Argument):
            parts.append(_format_argument(param))
        elif isinstance(param, click.Option):
            rendered = _format_option(param)
            if rendered not in ("--help", "--version", "--tree"):
                parts.append(rendered)
    return " " + " ".join(parts) if parts else ""


def _short_help(command: click.Command) -> str:
    return (command.short_help or command.help or "").strip().rstrip(".")


def _group_items(group: click.Group) -> list[tuple[str, str | click.Command]]:
    items: list[tuple[str, str | click.Command]] = []
    if group is main:
        items.extend([
            ("--help", "Show help for the current command"),
            ("--version", "Show package version"),
            ("--tree", "Print the registered CLI tree"),
        ])
    else:
        for param in group.params:
            if isinstance(param, click.Option):
                rendered = _format_option(param)
                if rendered != "--help":
                    items.append((rendered, (param.help or "").strip().rstrip(".")))
    for name, command in group.commands.items():
        if command.hidden:
            continue
        items.append((name, command))
    return items


def render_cli_tree(root: click.Group | None = None) -> str:
    """Render the visible registered Click command tree."""

    if root is None:
        root = main
    lines = [f"{root.name or 'chatlinux'} # {_short_help(root)}"]

    def walk(items: list[tuple[str, str | click.Command]], prefix: str = "") -> None:
        for index, (name, item) in enumerate(items):
            last = index == len(items) - 1
            branch = "└──" if last else "├──"
            next_prefix = prefix + ("    " if last else "│   ")
            if isinstance(item, str):
                suffix = f" # {item}" if item else ""
                lines.append(f"{prefix}{branch} {name}{suffix}")
                continue
            signature = _command_signature(item)
            help_text = _short_help(item)
            suffix = f" # {help_text}" if help_text else ""
            lines.append(f"{prefix}{branch} {name}{signature}{suffix}")
            if isinstance(item, click.Group):
                walk(_group_items(item), next_prefix)

    walk(_group_items(root))
    return "\n".join(lines)


def _tree_callback(ctx: click.Context, _param: click.Parameter, value: bool) -> None:
    if not value or ctx.resilient_parsing:
        return
    if not isinstance(ctx.command, click.Group):
        raise click.ClickException("--tree is only available on command groups")
    click.echo(render_cli_tree(ctx.command))
    ctx.exit()


@click.group(name="chatlinux")
@click.version_option(__version__, prog_name="chatlinux")
@click.option("--tree", is_flag=True, is_eager=True, expose_value=False, callback=_tree_callback, help="Print the registered CLI tree.")
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
