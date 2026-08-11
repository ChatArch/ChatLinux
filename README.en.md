<div align="center">
    <a href="https://pypi.python.org/pypi/ChatLinux">
        <img src="https://img.shields.io/pypi/v/ChatLinux.svg" alt="PyPI version" />
    </a>
    <a href="https://github.com/ChatArch/ChatLinux/actions/workflows/ci.yml">
        <img src="https://github.com/ChatArch/ChatLinux/actions/workflows/ci.yml/badge.svg" alt="Tests" />
    </a>
    <a href="https://arch.gh.wzhecnu.cn/ChatLinux/">
        <img src="https://img.shields.io/badge/docs-mkdocs-blue.svg" alt="Documentation" />
    </a>
</div>

<div align="center">

[English](README.en.md) | [简体中文](README.md)
</div>

# ChatLinux

ChatArch Linux operations package. Its first domain capability is a fleet status cache CLI: track servers with ChatArch-owned config, refresh common metrics through Ansible, and read the normalized local cache quickly from a shell.

Documentation entry: <https://arch.gh.wzhecnu.cn/ChatLinux/en/>

Choose documentation by scenario:

| Scenario | Document |
| --- | --- |
| Install, initialize the `.cube` track, refresh, and read cache | [Quick Start](docs/quickstart.en.md) |
| Inspect the implemented CLI tree and shell usage | [CLI Tree](docs/cli-tree.en.md) |
| Check first-class capabilities and current boundaries | [Capability Map](docs/capability-map.en.md) |
| Call package behavior directly from Python | [Interface Tree](docs/interface-tree.en.md) |

## Quick Start

```bash
pip install ChatLinux
chatlinux --version
chatlinux fleet init --sample cube
chatlinux fleet refresh --track cube
chatlinux fleet show --track cube
```

From a development checkout:

```bash
pip install -e ".[dev,docs]"
PYTHONPATH=src python -m pytest -q
PYTHONPATH=src python -m chatlinux.cli fleet --help
```

## Fleet Config and Cache

The default local state root is ChatArch-internal: `CHATLINUX_HOME` when set, otherwise `$CHATARCH_HOME/chatlinux`, and finally `~/.chatarch/chatlinux`. Default local paths include:

```text
~/.chatarch/chatlinux/fleet.json
~/.chatarch/chatlinux/cache/<track>-status.json
~/.chatarch/chatlinux/runtime/fleet-inventory.ini
~/.chatarch/chatlinux/runtime/fleet_probe.py
```

`runtime/` only stores the generated Ansible inventory and read-only probe for refresh runs. It still lives inside ChatArch home and does not write to `/etc`, `/usr`, system service directories, or the task repository. The ChatEnv provider namespace is also lowercase `chatlinux`, so future ChatEnv-managed values stay under ChatArch home instead of scattered workspace files.

`chatlinux fleet init --json` reports the full `state_paths` object, making it easy to verify config/cache/runtime placement under the same state root.

Use `--home` for task-local or CI state:

```bash
chatlinux fleet --home ./playground/chatlinux-home init --sample cube --json
chatlinux fleet --home ./playground/chatlinux-home status --track cube --refresh
```

## Safety Boundary

- `show` / `status` reads local cache by default; only `refresh` and `status --refresh` contact hosts.
- The MVP collects common public metrics only: CPU/load, memory, swap, filesystems, available GPU information, and failed systemd units.
- No sudo, cleanup, restart, or remote repair.

## CLI Contract

This package depends on `chatstyle>=0.1.0,<0.2.0` and `chatenv>=0.2.4,<0.3.0`. New commands should prefer:

- `CommandSchema` / `CommandField` for inputs.
- `add_interactive_option()` for the shared `-i/-I` switch.
- `resolve_command_inputs()` for missing args, defaults, TTY behavior, and validation.
- Keep `config.py` and a `chatenv.configs` entry point so the package remains ChatEnv-discoverable.

## Layout

- `src/`: package source code
- `tests/`: code and CLI tests
- `docs/`: long-lived project docs built by mkdocs

## Development Notes

See `DEVELOP.md` and `AGENTS.md` before expanding the package.
