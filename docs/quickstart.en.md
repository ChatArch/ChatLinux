# Quick Start

This page shows the smallest working ChatLinux fleet-status flow: initialize a track config, refresh the Ansible-backed cache once, then read the cached status quickly from a shell.

## Flow Entry Points

<div class="grid cards" markdown>

- **Install and Verify**

    Install the package and confirm `chatlinux --version` plus `chatlinux fleet --help` work.

    [Jump to install](#install-verify)

- **Initialize Internal State**

    Write `fleet.json` and prepare `cache/` plus `runtime/`. By default all three live under `~/.chatarch/chatlinux/`.

    [Jump to initialization](#init-cube-track)

- **Refresh Remote Status**

    Use Ansible to generate inventory/probe files, collect common read-only metrics, and write the local cache.

    [Jump to refresh](#refresh-status)

- **Read Cache / Safety Boundary**

    `show` / `status` read cache by default; remote sampling is explicit through `refresh` or `status --refresh`.

    [Jump to cache reads](#read-cache)

</div>

## Install and Verify {#install-verify}

```bash
pip install ChatLinux
chatlinux --version
chatlinux fleet --help
```

From a development checkout:

```bash
python -m pip install -e ".[dev,docs]"
PYTHONPATH=src python -m chatlinux.cli fleet --help
```

## Initialize the `.cube` Track {#init-cube-track}

The default state directory lives inside ChatArch home: `CHATLINUX_HOME` when set, otherwise `$CHATARCH_HOME/chatlinux`, and finally `~/.chatarch/chatlinux/`. Write the sample config first:

```bash
chatlinux fleet init --sample cube --json
```

The JSON output includes the full `state_paths` object, making every local state path auditable under the same ChatArch state root. This creates or uses:

```text
~/.chatarch/chatlinux/fleet.json
~/.chatarch/chatlinux/cache/
~/.chatarch/chatlinux/runtime/
```

`runtime/` stores the generated `fleet-inventory.ini` and `fleet_probe.py` for refresh runs. These files still live inside ChatArch home and are not written to `/etc`, `/usr`, system service directories, or the task repository.

For task-local or CI state, override the home directory:

```bash
chatlinux fleet --home ./playground/chatlinux-home init --sample cube --json
```

## Refresh Status {#refresh-status}

`refresh` reads the track config, renders an Ansible inventory and a read-only probe script, runs Ansible, and writes a normalized cache.

```bash
chatlinux fleet refresh --track cube
```

Machine-readable output:

```bash
chatlinux fleet refresh --track cube --json
```

The current sample track defaults to:

```text
uvx --from ansible-core ansible
```

and uses the remote Python validated during the `.cube` audit:

```text
/home/zhihong/.chatarch/venv/bin/python
```

## Read the Last Cache {#read-cache}

Reading cached status does not contact hosts, so it is fast for shell checks:

```bash
chatlinux fleet show --track cube
chatlinux fleet status --track cube
```

Refresh first and then display:

```bash
chatlinux fleet status --track cube --refresh
```

## Current Metrics

The MVP collects only common, easy, read-only metrics:

- hostname, sample time, uptime, CPU count, and load average;
- memory total/available and swap total/used;
- filesystem capacity from `df -P -T`;
- GPU count/model/memory/utilization when `nvidia-smi` is available;
- failed systemd unit names from `systemctl --failed`.

## Safety Boundary

- No sudo.
- No cleanup, restart, or remote repair.
- `show` / `status` reads cache by default; only `refresh` or `status --refresh` contacts hosts.
- SMART/NVMe lifetime data is not collected yet; it needs an explicit fleet helper or read-only sudo authorization.
