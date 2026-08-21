from click.testing import CliRunner

from chatlinux import __version__
from chatlinux.cli import main


def test_version_option_reports_package_version():
    result = CliRunner().invoke(main, ["--version"])

    assert result.exit_code == 0
    assert f"chatlinux, version {__version__}" in result.output


def test_help_lists_tree_option_and_fleet_group():
    result = CliRunner().invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "--tree" in result.output
    assert "--tree-brief" in result.output
    assert "fleet" in result.output
    assert "hello" not in result.output.lower()


def test_tree_option_renders_canonical_root_and_parameter_signatures():
    result = CliRunner().invoke(main, ["--tree"])

    assert result.exit_code == 0, result.output
    assert result.output.splitlines()[0] == "chatlinux"
    assert "├── --help" in result.output
    assert "├── --version" in result.output
    assert "├── --tree" in result.output
    assert "├── --tree-brief" in result.output
    assert "└── fleet [--home HOME]" in result.output
    assert "    ├── init [--sample SAMPLE] [--force] [--json]" in result.output
    assert "    ├── refresh [--track TRACK] [--json]" in result.output
    assert "    ├── show [--track TRACK] [--json]" in result.output
    assert "    └── status [--track TRACK] [--refresh] [--json]" in result.output
    assert "hello" not in result.output.lower()


def test_tree_brief_omits_signatures_but_keeps_commands_and_descriptions():
    result = CliRunner().invoke(main, ["--tree-brief"])

    assert result.exit_code == 0, result.output
    assert result.output.splitlines()[0] == "chatlinux"
    assert "└── fleet  # Track server fleets and view cached health status." in result.output
    assert "    ├── init  # Initialize a fleet config under the ChatLinux state directory." in result.output
    assert "    ├── refresh  # Run Ansible read-only checks and update the local cache." in result.output
    assert "    ├── show  # Show the last cached fleet status without contacting hosts." in result.output
    assert "    └── status  # Show cached fleet status, optionally refreshing first." in result.output
    assert "[--home HOME]" not in result.output
    assert "[--sample SAMPLE]" not in result.output
    assert "[--track TRACK]" not in result.output
