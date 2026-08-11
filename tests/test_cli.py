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
    assert "fleet" in result.output
    assert "hello" not in result.output.lower()


def test_tree_option_renders_registered_fleet_command_surface():
    result = CliRunner().invoke(main, ["--tree"])

    assert result.exit_code == 0, result.output
    assert "chatlinux # chatlinux command line interface" in result.output
    assert "├── --help" in result.output
    assert "├── --version" in result.output
    assert "├── --tree" in result.output
    assert "└── fleet" in result.output
    assert "--home" in result.output
    assert "    ├── init" in result.output
    assert "    ├── refresh" in result.output
    assert "    ├── show" in result.output
    assert "    └── status" in result.output
    assert "hello" not in result.output.lower()
