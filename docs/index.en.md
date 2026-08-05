# ChatLinux Docs

ChatLinux is a ChatArch Linux operations package. Its first domain capability is a **fleet status cache CLI**: track servers with ChatArch-owned config, refresh common metrics through Ansible, and read the normalized local cache quickly from a shell.

Site entry: <https://arch.gh.wzhecnu.cn/ChatLinux/en/>

## Choose Documentation by Scenario

| Scenario | Document |
| --- | --- |
| Install, initialize the `.cube` track, refresh, and read cache | [Quick Start](quickstart.md) |
| Inspect the implemented CLI tree and shell usage | [CLI Tree](cli-tree.md) |
| Check first-class capabilities and current boundaries | [Capability Map](capability-map.md) |
| Call package behavior directly from Python | [Python Interface Tree](interface-tree.md) |

## Primary Entry Points

<div class="grid cards" markdown>

- **Quick Start**

    Initialize `fleet.json`, refresh `.cube` status, and read the cached result quickly.

    [Open Quick Start](quickstart.md)

- **CLI Tree**

    Start from the CLI entry point and record implemented commands, command status, and interactive conventions.

    [Open CLI Tree](cli-tree.md)

- **Capability Map**

    Review current package boundaries and avoid presenting planned work as implemented behavior.

    [Open Capability Map](capability-map.md)

- **Python Interface Tree**

    Keep the CLI thin and put substantive behavior in importable Python APIs.

    [Open Interface Tree](interface-tree.md)

</div>

## Current Default Paths

Default local state root: `CHATLINUX_HOME` > `$CHATARCH_HOME/chatlinux` > `~/.chatarch/chatlinux`. Default paths:

```text
~/.chatarch/chatlinux/fleet.json
~/.chatarch/chatlinux/cache/<track>-status.json
~/.chatarch/chatlinux/runtime/fleet-inventory.ini
~/.chatarch/chatlinux/runtime/fleet_probe.py
```

`show` / `status` reads cache by default; only `refresh` and `status --refresh` contact hosts. `init --json` reports the full `state_paths` object so config/cache/runtime placement is directly auditable.

## Local Preview

```bash
python -m pip install -e ".[docs]"
mkdocs serve
```

The Chinese home page is available at <https://arch.gh.wzhecnu.cn/ChatLinux/>.
