# CLI Tree

This page shows the currently implemented `ChatLinux` command tree. Importable Python functions are mapped in [Python Interface Tree](interface-tree.md), and package boundaries are tracked in [Capability Map](capability-map.md).

## Top-Level Commands

```text
chatlinux                         # ChatLinux command-line entry
├── --help                            # Show CLI help and registered commands
├── --version                         # Print the current package version
└── fleet                             # Manage and view cached fleet status
```

## Fleet Status Commands

```text
chatlinux fleet                   # Server fleet status command group
├── --home DIRECTORY                  # Override the ChatLinux state directory; defaults to ~/.chatarch/chatlinux
├── init                              # Initialize fleet config, cache, and runtime directories
│   ├── --sample cube                 # Write the ChatArch .cube sample track
│   ├── --force                       # Overwrite an existing config
│   └── --json                        # Print machine-readable JSON with full state_paths
├── refresh                           # Run read-only Ansible checks and write cache
│   ├── --track cube                  # Select the track to refresh
│   └── --json                        # Print the full cache JSON
├── show                              # Show the last cache without contacting hosts
│   ├── --track cube                  # Select the track to read
│   └── --json                        # Print cache JSON
└── status                            # Same as show by default; can refresh first
    ├── --track cube                  # Select the track
    ├── --refresh                     # Run refresh before display
    └── --json                        # Print JSON
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
