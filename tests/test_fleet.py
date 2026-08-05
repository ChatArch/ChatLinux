import json
from dataclasses import dataclass

from click.testing import CliRunner

from chatlinux.cli import main


CUBE_HOSTS = [
    "auc.cube",
    "bleu.cube",
    "f1.cube",
    "hitk.cube",
    "map.cube",
    "precision.cube",
    "recall.cube",
]


def test_fleet_init_writes_cube_track_config(tmp_path):
    result = CliRunner().invoke(
        main,
        ["fleet", "--home", str(tmp_path), "init", "--sample", "cube", "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["config_path"] == str(tmp_path / "fleet.json")
    assert payload["state_paths"] == {
        "home": str(tmp_path),
        "config": str(tmp_path / "fleet.json"),
        "cache_dir": str(tmp_path / "cache"),
        "runtime_dir": str(tmp_path / "runtime"),
        "inventory": str(tmp_path / "runtime" / "fleet-inventory.ini"),
        "probe": str(tmp_path / "runtime" / "fleet_probe.py"),
        "cache": str(tmp_path / "cache" / "cube-status.json"),
    }

    config = json.loads((tmp_path / "fleet.json").read_text())
    assert config["default_track"] == "cube"
    track = config["tracks"]["cube"]
    assert track["hosts"] == CUBE_HOSTS
    assert track["checks"] == ["system", "memory", "disk", "gpu", "services"]
    assert track["ansible"]["python_interpreter"] == "/home/zhihong/.chatarch/venv/bin/python"


def test_default_fleet_state_paths_are_under_chatarch_home(monkeypatch, tmp_path):
    from chatlinux.fleet import default_home, init_config, state_paths

    chatarch_home = tmp_path / ".chatarch"
    monkeypatch.delenv("CHATLINUX_HOME", raising=False)
    monkeypatch.setenv("CHATARCH_HOME", str(chatarch_home))

    assert default_home() == chatarch_home / "chatlinux"
    paths = state_paths()
    assert paths == {
        "home": chatarch_home / "chatlinux",
        "config": chatarch_home / "chatlinux" / "fleet.json",
        "cache_dir": chatarch_home / "chatlinux" / "cache",
        "runtime_dir": chatarch_home / "chatlinux" / "runtime",
        "inventory": chatarch_home / "chatlinux" / "runtime" / "fleet-inventory.ini",
        "probe": chatarch_home / "chatlinux" / "runtime" / "fleet_probe.py",
        "cache": chatarch_home / "chatlinux" / "cache" / "cube-status.json",
    }

    init_config(sample="cube")
    assert paths["config"].exists()
    assert paths["cache_dir"].is_dir()
    assert paths["runtime_dir"].is_dir()
    assert not (tmp_path / "fleet.json").exists()


def test_chatenv_provider_uses_lowercase_chatarch_storage_namespace():
    from chatlinux.config import ChatlinuxConfig

    assert ChatlinuxConfig._aliases == ["chatlinux"]
    assert ChatlinuxConfig._storage_dir == "chatlinux"


def test_fleet_help_documents_chatarch_internal_default_home():
    result = CliRunner().invoke(main, ["fleet", "--help"])

    assert result.exit_code == 0, result.output
    assert "CHATLINUX_HOME" in result.output
    assert "CHATARCH_HOME/chatlinux" in result.output
    assert "~/.chatarch/chatlinux" in result.output


def test_fleet_show_reads_last_cache_without_refreshing(tmp_path):
    cache_path = tmp_path / "cache" / "cube-status.json"
    cache_path.parent.mkdir(parents=True)
    cache_path.write_text(
        json.dumps(
            {
                "version": 1,
                "track": "cube",
                "generated_at": "2026-08-05T07:00:00+08:00",
                "hosts": {
                    "auc.cube": {
                        "ok": True,
                        "hostname": "auc",
                        "cpu_count": 32,
                        "load": {"1m": 0.12, "5m": 0.2, "15m": 0.3},
                        "memory": {"available_bytes": 123456789},
                        "filesystems": [],
                        "gpus": [],
                        "failed_units": [],
                    }
                },
            }
        )
    )

    result = CliRunner().invoke(
        main,
        ["fleet", "--home", str(tmp_path), "show", "--track", "cube", "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["track"] == "cube"
    assert payload["hosts"]["auc.cube"]["hostname"] == "auc"


@dataclass
class FakeCompletedProcess:
    args: list[str]
    returncode: int
    stdout: str
    stderr: str = ""


def test_refresh_track_runs_ansible_and_writes_normalized_cache(tmp_path):
    from chatlinux.fleet import init_config, refresh_track

    init_config(tmp_path, sample="cube")
    calls = []

    def fake_runner(args, *, capture_output, text, check):
        calls.append(args)
        assert capture_output is True
        assert text is True
        assert check is False
        stdout_payload = json.dumps(
            {
                "hostname": "auc",
                "sampled_at": "2026-08-05T07:01:00+08:00",
                "uptime_seconds": 3600,
                "cpu_count": 32,
                "load": {"1m": 0.1, "5m": 0.2, "15m": 0.3},
                "memory": {"total_bytes": 64_000, "available_bytes": 32_000},
                "swap": {"total_bytes": 0, "used_bytes": 0},
                "filesystems": [],
                "gpus": [],
                "failed_units": [],
            }
        )
        return FakeCompletedProcess(
            args=args,
            returncode=0,
            stdout='auc.cube | CHANGED => '
            + json.dumps({"changed": True, "rc": 0, "stdout": stdout_payload, "stderr": ""})
            + "\n",
        )

    snapshot = refresh_track(tmp_path, track="cube", runner=fake_runner)

    probe_script = tmp_path / "runtime" / "fleet_probe.py"
    assert probe_script.read_text().splitlines()[0] == "#!/home/zhihong/.chatarch/venv/bin/python"
    assert calls, "refresh_track should call the configured Ansible command"
    assert calls[0][:3] == ["uvx", "--from", "ansible-core"]
    assert "-m" in calls[0]
    assert snapshot["track"] == "cube"
    assert snapshot["ansible_exit_code"] == 0
    assert snapshot["hosts"]["auc.cube"]["ok"] is True
    assert snapshot["hosts"]["auc.cube"]["hostname"] == "auc"

    cached = json.loads((tmp_path / "cache" / "cube-status.json").read_text())
    assert cached["hosts"]["auc.cube"]["cpu_count"] == 32


def test_fleet_status_table_summarizes_cached_hosts(tmp_path):
    cache_path = tmp_path / "cache" / "cube-status.json"
    cache_path.parent.mkdir(parents=True)
    cache_path.write_text(
        json.dumps(
            {
                "version": 1,
                "track": "cube",
                "generated_at": "2026-08-05T07:00:00+08:00",
                "hosts": {
                    "auc.cube": {
                        "ok": True,
                        "hostname": "auc",
                        "cpu_count": 32,
                        "load": {"1m": 0.12, "5m": 0.2, "15m": 0.3},
                        "memory": {"available_bytes": 123456789},
                        "filesystems": [],
                        "gpus": [],
                        "failed_units": [],
                    },
                    "precision.cube": {"ok": False, "error": "nvidia-smi failed"},
                },
            }
        )
    )

    result = CliRunner().invoke(
        main,
        ["fleet", "--home", str(tmp_path), "status", "--track", "cube"],
    )

    assert result.exit_code == 0, result.output
    assert "auc.cube" in result.output
    assert "precision.cube" in result.output
    assert "nvidia-smi failed" in result.output


def test_parse_systemd_failed_unit_handles_bullet_prefix():
    from chatlinux.fleet import parse_systemd_failed_unit

    assert parse_systemd_failed_unit("● nginx.service loaded failed failed A web server") == "nginx.service"
    assert parse_systemd_failed_unit("snap.certbot.renew.service loaded failed failed") == "snap.certbot.renew.service"
    assert parse_systemd_failed_unit("   ") is None
