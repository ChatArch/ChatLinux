# Capability Map

Use this page to check which first-class capabilities `ChatLinux` currently owns, which ones are verified, and what remains out of scope for this package.

## Capability Groups

<div class="grid cards" markdown>

- **Fleet Status Cache**

    Track a set of Linux servers with a config file, refresh common metrics through Ansible, and keep config, cache, and runtime inventory/probe files under ChatArch home.

- **CLI Entry**

    `chatlinux fleet init/refresh/show/status` provides shell-friendly operations; `show` reads the local cache by default.

- **Python API**

    Substantive behavior lives in `chatlinux.fleet`; Click commands only parse arguments and render output.

- **Config and Environment**

    The default state root is `CHATLINUX_HOME` > `$CHATARCH_HOME/chatlinux` > `~/.chatarch/chatlinux/`, containing `fleet.json`, `cache/`, and `runtime/`. `init --json` reports the full `state_paths` object.

</div>

## Current Boundary

| Capability | Status | Notes |
| --- | --- | --- |
| CLI base entry | Implemented | Click group, `--version`, and base tests. |
| ChatEnv provider | Implemented | `config.py` and the `chatenv.configs` entry point remain discoverable by ChatEnv. |
| Fleet sample config | Implemented | `chatlinux fleet init --sample cube` writes the `.cube` track. |
| Fleet refresh | Implemented | `chatlinux fleet refresh --track cube` renders Ansible inventory/probe files, runs read-only checks, and writes cache. |
| Fleet cache view | Implemented | `show` / `status` read `cache/<track>-status.json` without contacting hosts. |
| JSON output | Implemented | `init`, `refresh`, `show`, and `status` support `--json`. |

## Current Metrics

- hostname, sample time, uptime, CPU count, and load average;
- memory total/available and swap total/used;
- filesystem capacity;
- GPU information when `nvidia-smi` is available;
- failed systemd unit names from `systemctl --failed`.

## Out of Scope

- No sudo.
- No cleanup, restart, or remote repair.
- No privileged SMART/NVMe lifetime data.
- Do not document unimplemented features as executable tutorials.
- Do not print secrets, tokens, cookies, or Authorization headers in README, docs, issues, PR comments, or CI logs.
