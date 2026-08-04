# Python Interface Tree

`ChatLinux` keeps the CLI thin. Substantive behavior lives in importable Python functions so future MCP tools, automation scripts, or other ChatArch packages can reuse it without shelling out.

## Package Entry

```python
from chatlinux import __version__
```

## Fleet Status APIs

```python
from chatlinux.fleet import (
    init_config,
    load_config,
    refresh_track,
    load_cache,
    format_table,
    state_paths,
)
```

| Function | Purpose |
| --- | --- |
| `state_paths(home=None, track="cube")` | Return `home`, `config`, `cache_dir`, `runtime_dir`, `inventory`, `probe`, and `cache`; by default all live under the same ChatArch state root. |
| `init_config(home=None, sample="cube", force=False)` | Initialize `fleet.json`, cache, and runtime directories. |
| `load_config(home=None)` | Read and validate fleet config. |
| `refresh_track(home=None, track="cube", runner=subprocess.run)` | Run read-only Ansible refresh, normalize results, and write cache. |
| `load_cache(home=None, track="cube")` | Read the last cache without contacting hosts. |
| `format_table(snapshot)` | Render cache JSON as a compact table. |
| `parse_ansible_output(output, expected_hosts=...)` | Parse Ansible `-o` script output. |

## Module Layout

```text
chatlinux
├── cli.py           # Click entry; argument parsing and output only
├── config.py        # ChatEnv provider
└── fleet.py         # fleet config, Ansible refresh, cache, and rendering logic
```

## Output Contract

- `refresh_track` returns a structured dict, writes `cache/<track>-status.json`, and generates `runtime/fleet-inventory.ini` plus `runtime/fleet_probe.py` under the same home.
- `load_cache` reads local cache only and is suitable for fast shell/status checks.
- Remote probe failures are preserved under each host's `ok=false` / `error` fields.
- Public output should not leak tokens, cookies, internal Authorization headers, or sensitive personal data.
