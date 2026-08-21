# CLI Tree

This page shows the currently implemented `ChatLinux` command tree. Importable Python functions are mapped in [Python Interface Tree](interface-tree.md), and package boundaries are tracked in [Capability Map](capability-map.md).

ChatStyle renders `chatlinux --tree` from the Click registry with parameter signatures by default; release acceptance uses this output:

```text
chatlinux
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
├── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
└── fleet [--home HOME]  # Track server fleets and view cached health status.
    ├── init [--sample SAMPLE] [--force] [--json]  # Initialize a fleet config under the ChatLinux state directory.
    ├── refresh [--track TRACK] [--json]  # Run Ansible read-only checks and update the local cache.
    ├── show [--track TRACK] [--json]  # Show the last cached fleet status without contacting hosts.
    └── status [--track TRACK] [--refresh] [--json]  # Show cached fleet status, optionally refreshing first.
```

`chatlinux --tree-brief` omits parameter signatures while keeping command nodes and descriptions:

```text
chatlinux
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
├── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
└── fleet  # Track server fleets and view cached health status.
    ├── init  # Initialize a fleet config under the ChatLinux state directory.
    ├── refresh  # Run Ansible read-only checks and update the local cache.
    ├── show  # Show the last cached fleet status without contacting hosts.
    └── status  # Show cached fleet status, optionally refreshing first.
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
