# CLI Tree

This page shows the currently implemented `ChatLinux` command tree. Importable Python functions are mapped in [Python Interface Tree](interface-tree.md), and package boundaries are tracked in [Capability Map](capability-map.md).

`chatlinux --tree` renders the real command tree from the Click registry; release acceptance uses this output:

```text
chatlinux # chatlinux command line interface
├── --help # Show help for the current command
├── --version # Show package version
├── --tree # Print the registered CLI tree
└── fleet # Track server fleets and view cached health status
    ├── [--home HOME] # ChatLinux state directory. Defaults to $CHATLINUX_HOME, then $CHATARCH_HOME/chatlinux, then ~/.chatarch/chatlinux
    ├── init [--sample SAMPLE] --force --json # Initialize a fleet config under the ChatLinux state directory
    ├── refresh [--track TRACK] --json # Run Ansible read-only checks and update the local cache
    ├── show [--track TRACK] --json # Show the last cached fleet status without contacting hosts
    └── status [--track TRACK] --refresh --json # Show cached fleet status, optionally refreshing first
```

## Common Shell Flow

```bash
chatlinux fleet init --sample cube
chatlinux fleet refresh --track cube
chatlinux fleet show --track cube
```

Use task-local state:

```bash
chatlinux fleet --home ./playground/chatlinux-home init --sample cube --json
chatlinux fleet --home ./playground/chatlinux-home status --track cube --refresh
```

## Status Contract

| Status | Meaning |
| --- | --- |
| Implemented | Command, function, and tests exist |
| Verified | Covered by local tests, shell smoke, or a real Ansible refresh |
| Planned / checkpoint | Keep only boundary notes; do not write operation tutorials before implementation |

## Update Checklist

- When adding commands, update the CLI tree, capability map, interface tree, README, tests, and changelog together.
- Commands that contact remote hosts must document whether they are read-only, whether they use sudo, and whether they write cache or remote state.
- `show` / `status` reads local cache by default; only `refresh` and `status --refresh` contact hosts.
