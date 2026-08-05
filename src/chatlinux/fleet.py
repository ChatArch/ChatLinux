"""Fleet status configuration, refresh, cache, and rendering helpers."""

from __future__ import annotations

import json
import os
import re
import subprocess
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

CUBE_HOSTS = [
    "auc.cube",
    "bleu.cube",
    "f1.cube",
    "hitk.cube",
    "map.cube",
    "precision.cube",
    "recall.cube",
]

STATE_DIR_NAME = "chatlinux"
CONFIG_FILENAME = "fleet.json"
CACHE_DIR_NAME = "cache"
RUNTIME_DIR_NAME = "runtime"
INVENTORY_FILENAME = "fleet-inventory.ini"
PROBE_FILENAME = "fleet_probe.py"

DEFAULT_CHECKS = ["system", "memory", "disk", "gpu", "services"]
DEFAULT_ANSIBLE_COMMAND = ["uvx", "--from", "ansible-core", "ansible"]
DEFAULT_REMOTE_PYTHON = "/home/zhihong/.chatarch/venv/bin/python"
DEFAULT_SSH_COMMON_ARGS = "-o BatchMode=yes -o ConnectTimeout=8"

Runner = Callable[..., subprocess.CompletedProcess[str]]


class FleetError(RuntimeError):
    """Raised when fleet configuration or cache operations fail."""


def default_home() -> Path:
    """Return the default ChatLinux state directory under ChatArch home."""

    explicit = os.environ.get("CHATLINUX_HOME")
    if explicit:
        return Path(explicit).expanduser()
    chatarch_home = Path(os.environ.get("CHATARCH_HOME", "~/.chatarch")).expanduser()
    return chatarch_home / STATE_DIR_NAME


def state_paths(home: str | Path | None = None, *, track: str = "cube") -> dict[str, Path]:
    """Return every local ChatLinux fleet state path under one state home."""

    base = Path(home).expanduser() if home else default_home()
    runtime = base / RUNTIME_DIR_NAME
    return {
        "home": base,
        "config": base / CONFIG_FILENAME,
        "cache_dir": base / CACHE_DIR_NAME,
        "runtime_dir": runtime,
        "inventory": runtime / INVENTORY_FILENAME,
        "probe": runtime / PROBE_FILENAME,
        "cache": base / CACHE_DIR_NAME / f"{track}-status.json",
    }


def config_path(home: str | Path | None = None) -> Path:
    return state_paths(home)["config"]


def cache_path(home: str | Path | None = None, track: str = "cube") -> Path:
    return state_paths(home, track=track)["cache"]


def sample_config(sample: str = "cube") -> dict[str, Any]:
    """Return a sample fleet configuration."""

    if sample != "cube":
        raise FleetError(f"Unsupported sample config: {sample}")
    return {
        "version": 1,
        "default_track": "cube",
        "tracks": {
            "cube": {
                "description": "ChatArch .cube servers",
                "hosts": list(CUBE_HOSTS),
                "checks": list(DEFAULT_CHECKS),
                "ansible": {
                    "command": list(DEFAULT_ANSIBLE_COMMAND),
                    "python_interpreter": DEFAULT_REMOTE_PYTHON,
                    "ssh_common_args": DEFAULT_SSH_COMMON_ARGS,
                },
            }
        },
    }


def init_config(home: str | Path | None = None, *, sample: str = "cube", force: bool = False) -> dict[str, Any]:
    """Create a fleet config plus cache/runtime directories under the state home."""

    paths = state_paths(home)
    path = paths["config"]
    path.parent.mkdir(parents=True, exist_ok=True)
    paths["cache_dir"].mkdir(parents=True, exist_ok=True)
    paths["runtime_dir"].mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        return load_config(path.parent)
    config = sample_config(sample)
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n")
    return config


def load_config(home: str | Path | None = None) -> dict[str, Any]:
    path = config_path(home)
    if not path.exists():
        raise FleetError(f"Fleet config not found: {path}. Run `chatlinux fleet init` first.")
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise FleetError(f"Invalid fleet config JSON: {path}: {exc}") from exc
    if not isinstance(data, dict) or "tracks" not in data:
        raise FleetError(f"Invalid fleet config: {path}")
    return data


def resolve_track(config: Mapping[str, Any], track: str | None = None) -> tuple[str, dict[str, Any]]:
    track_name = track or str(config.get("default_track") or "")
    tracks = config.get("tracks")
    if not isinstance(tracks, Mapping) or track_name not in tracks:
        raise FleetError(f"Unknown fleet track: {track_name}")
    track_config = tracks[track_name]
    if not isinstance(track_config, dict):
        raise FleetError(f"Invalid fleet track config: {track_name}")
    hosts = track_config.get("hosts")
    if not isinstance(hosts, list) or not hosts:
        raise FleetError(f"Fleet track has no hosts: {track_name}")
    return track_name, track_config


def write_inventory(home: str | Path, track_config: Mapping[str, Any]) -> Path:
    """Render an Ansible inventory file for one track."""

    paths = state_paths(home)
    paths["runtime_dir"].mkdir(parents=True, exist_ok=True)
    path = paths["inventory"]
    raw_ansible = track_config.get("ansible")
    ansible = raw_ansible if isinstance(raw_ansible, Mapping) else {}
    python_interpreter = ansible.get("python_interpreter") or DEFAULT_REMOTE_PYTHON
    ssh_common_args = ansible.get("ssh_common_args") or DEFAULT_SSH_COMMON_ARGS
    lines = ["[fleet]"]
    lines.extend(str(host) for host in track_config["hosts"])
    lines.extend(
        [
            "",
            "[fleet:vars]",
            "ansible_connection=ssh",
            f"ansible_python_interpreter={python_interpreter}",
            f"ansible_ssh_common_args='{ssh_common_args}'",
            "",
        ]
    )
    path.write_text("\n".join(lines))
    return path


def probe_script_text(python_interpreter: str = DEFAULT_REMOTE_PYTHON) -> str:
    """Return the remote read-only probe script used by Ansible script mode."""

    body = textwrap.dedent(
        r'''
        import json
        import os
        import socket
        import subprocess
        from datetime import datetime, timezone


        def run(args):
            try:
                return subprocess.run(args, capture_output=True, text=True, check=False, timeout=12)
            except Exception as exc:
                return type("Result", (), {"returncode": -1, "stdout": "", "stderr": str(exc)})()


        def meminfo():
            data = {}
            try:
                with open("/proc/meminfo", "r", encoding="utf-8") as handle:
                    for line in handle:
                        name, value = line.split(":", 1)
                        parts = value.strip().split()
                        if parts:
                            data[name] = int(parts[0]) * 1024
            except Exception:
                return {}, {}
            memory = {
                "total_bytes": data.get("MemTotal"),
                "available_bytes": data.get("MemAvailable"),
                "free_bytes": data.get("MemFree"),
            }
            swap_total = data.get("SwapTotal") or 0
            swap_free = data.get("SwapFree") or 0
            swap = {"total_bytes": swap_total, "used_bytes": max(swap_total - swap_free, 0)}
            return memory, swap


        def uptime_seconds():
            try:
                with open("/proc/uptime", "r", encoding="utf-8") as handle:
                    return float(handle.read().split()[0])
            except Exception:
                return None


        def filesystems():
            result = run(["df", "-P", "-T"])
            rows = []
            if result.returncode != 0:
                return rows
            for line in result.stdout.splitlines()[1:]:
                parts = line.split()
                if len(parts) < 7:
                    continue
                percent_text = parts[5].rstrip("%")
                try:
                    percent = int(percent_text)
                except ValueError:
                    percent = None
                rows.append(
                    {
                        "source": parts[0],
                        "fstype": parts[1],
                        "total_bytes": int(parts[2]) * 1024,
                        "used_bytes": int(parts[3]) * 1024,
                        "available_bytes": int(parts[4]) * 1024,
                        "used_percent": percent,
                        "mount": " ".join(parts[6:]),
                    }
                )
            return rows


        def gpus():
            query = "index,name,memory.total,memory.used,utilization.gpu"
            result = run([
                "nvidia-smi",
                f"--query-gpu={query}",
                "--format=csv,noheader,nounits",
            ])
            if result.returncode != 0:
                return [], (result.stderr.strip() or "nvidia-smi unavailable")
            rows = []
            for line in result.stdout.splitlines():
                parts = [part.strip() for part in line.split(",")]
                if len(parts) != 5:
                    continue
                rows.append(
                    {
                        "index": parts[0],
                        "name": parts[1],
                        "memory_total_mib": _int_or_none(parts[2]),
                        "memory_used_mib": _int_or_none(parts[3]),
                        "utilization_gpu_percent": _int_or_none(parts[4]),
                    }
                )
            return rows, None


        def failed_units():
            result = run(["systemctl", "--failed", "--no-legend", "--no-pager"])
            units = []
            for line in result.stdout.splitlines():
                parts = line.split()
                if not parts:
                    continue
                if parts[0] == "●" and len(parts) > 1:
                    units.append(parts[1])
                else:
                    units.append(parts[0])
            return units


        def _int_or_none(value):
            try:
                return int(value)
            except Exception:
                return None


        memory, swap = meminfo()
        gpu_rows, gpu_error = gpus()
        load1, load5, load15 = os.getloadavg()
        payload = {
            "hostname": socket.gethostname(),
            "sampled_at": datetime.now(timezone.utc).astimezone().isoformat(),
            "uptime_seconds": uptime_seconds(),
            "cpu_count": os.cpu_count(),
            "load": {"1m": load1, "5m": load5, "15m": load15},
            "memory": memory,
            "swap": swap,
            "filesystems": filesystems(),
            "gpus": gpu_rows,
            "failed_units": failed_units(),
        }
        if gpu_error:
            payload["gpu_error"] = gpu_error
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        '''
    ).strip() + "\n"
    return f"#!{python_interpreter}\n" + body


def write_probe_script(home: str | Path, *, python_interpreter: str = DEFAULT_REMOTE_PYTHON) -> Path:
    paths = state_paths(home)
    paths["runtime_dir"].mkdir(parents=True, exist_ok=True)
    path = paths["probe"]
    path.write_text(probe_script_text(python_interpreter))
    return path


def refresh_track(
    home: str | Path | None = None,
    *,
    track: str | None = None,
    runner: Runner = subprocess.run,
) -> dict[str, Any]:
    """Run the configured Ansible refresh and write the normalized cache."""

    base = Path(home).expanduser() if home else default_home()
    config = load_config(base)
    track_name, track_config = resolve_track(config, track)
    inventory = write_inventory(base, track_config)
    raw_ansible = track_config.get("ansible")
    ansible = raw_ansible if isinstance(raw_ansible, Mapping) else {}
    python_interpreter = str(ansible.get("python_interpreter") or DEFAULT_REMOTE_PYTHON)
    probe = write_probe_script(base, python_interpreter=python_interpreter)
    command = list(ansible.get("command") or DEFAULT_ANSIBLE_COMMAND)
    args = command + ["fleet", "-i", str(inventory), "-m", "script", "-a", str(probe), "-o"]
    completed = runner(args, capture_output=True, text=True, check=False)
    hosts = parse_ansible_output(completed.stdout, expected_hosts=track_config["hosts"])
    if not hosts and completed.returncode != 0:
        raise FleetError(completed.stderr.strip() or "Ansible refresh failed without parseable host output")
    snapshot = {
        "version": 1,
        "track": track_name,
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "source": "ansible",
        "config_path": str(config_path(base)),
        "inventory_path": str(inventory),
        "probe_path": str(probe),
        "ansible_exit_code": completed.returncode,
        "hosts": hosts,
    }
    if completed.stderr.strip():
        snapshot["ansible_stderr"] = completed.stderr.strip()
    path = cache_path(base, track_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return snapshot


def parse_ansible_output(output: str, *, expected_hosts: Sequence[str] = ()) -> dict[str, Any]:
    """Parse one-line Ansible `-o` script output into per-host records."""

    hosts: dict[str, Any] = {}
    seen: set[str] = set()
    pattern = re.compile(r"^(?P<host>\S+)\s+\|\s+(?P<state>.+?)\s+=>\s+(?P<payload>\{.*\})$")
    for line in output.splitlines():
        match = pattern.match(line.strip())
        if not match:
            continue
        host = match.group("host")
        seen.add(host)
        try:
            payload = json.loads(match.group("payload"))
        except json.JSONDecodeError:
            hosts[host] = {"ok": False, "error": "invalid ansible JSON payload"}
            continue
        if payload.get("unreachable"):
            hosts[host] = {"ok": False, "error": payload.get("msg") or "unreachable"}
            continue
        rc = payload.get("rc", 0)
        stdout = payload.get("stdout") or ""
        try:
            metrics = json.loads(stdout.strip()) if stdout.strip() else {}
        except json.JSONDecodeError:
            metrics = {"raw_stdout": stdout.strip()} if stdout.strip() else {}
        if rc != 0:
            error = payload.get("stderr") or payload.get("msg") or f"probe rc={rc}"
            hosts[host] = {"ok": False, "error": str(error).strip(), **metrics}
        else:
            hosts[host] = {"ok": True, **metrics}
    for host in expected_hosts:
        if host not in seen:
            hosts[str(host)] = {"ok": False, "error": "missing from ansible output"}
    return hosts


def parse_systemd_failed_unit(line: str) -> str | None:
    """Extract a unit name from one `systemctl --failed --no-legend` output line."""

    parts = line.split()
    if not parts:
        return None
    if parts[0] == "●" and len(parts) > 1:
        return parts[1]
    return parts[0]


def load_cache(home: str | Path | None = None, *, track: str = "cube") -> dict[str, Any]:
    path = cache_path(home, track)
    if not path.exists():
        raise FleetError(f"Fleet cache not found: {path}. Run `chatlinux fleet refresh --track {track}` first.")
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise FleetError(f"Invalid fleet cache JSON: {path}: {exc}") from exc


def format_table(snapshot: Mapping[str, Any]) -> str:
    """Render a compact status table for humans."""

    lines = [f"Fleet track: {snapshot.get('track')}  generated_at: {snapshot.get('generated_at')}"]
    lines.append("HOST                 OK  CPU  LOAD1   MEM_AVAIL  GPU  FAILED_UNITS  NOTE")
    raw_hosts = snapshot.get("hosts")
    hosts = raw_hosts if isinstance(raw_hosts, Mapping) else {}
    for host, data in hosts.items():
        row = data if isinstance(data, Mapping) else {}
        ok = "yes" if row.get("ok") else "no"
        cpu = _text(row.get("cpu_count"))
        load_data = row.get("load")
        load1 = load_data.get("1m") if isinstance(load_data, Mapping) else None
        load = f"{load1:.2f}" if isinstance(load1, (int, float)) else "-"
        memory_data = row.get("memory")
        memory = memory_data if isinstance(memory_data, Mapping) else {}
        mem_avail = _human_bytes(memory.get("available_bytes"))
        gpus = row.get("gpus") if isinstance(row.get("gpus"), list) else []
        gpu_text = str(len(gpus)) if gpus else ("0" if row.get("gpu_error") else "-")
        failed = row.get("failed_units") if isinstance(row.get("failed_units"), list) else []
        failed_text = str(len(failed)) if failed else "0"
        note = row.get("error") or row.get("gpu_error") or ""
        lines.append(f"{host:<20} {ok:<3} {cpu:<4} {load:<7} {mem_avail:<10} {gpu_text:<4} {failed_text:<13} {note}")
    return "\n".join(lines) + "\n"


def _text(value: Any) -> str:
    return "-" if value is None else str(value)


def _human_bytes(value: Any) -> str:
    if not isinstance(value, (int, float)):
        return "-"
    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
    size = float(value)
    for unit in units:
        if abs(size) < 1024.0 or unit == units[-1]:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}PiB"


__all__ = [
    "CUBE_HOSTS",
    "DEFAULT_CHECKS",
    "FleetError",
    "cache_path",
    "config_path",
    "default_home",
    "format_table",
    "init_config",
    "load_cache",
    "load_config",
    "parse_ansible_output",
    "refresh_track",
    "sample_config",
    "state_paths",
]
