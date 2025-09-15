from typer.testing import CliRunner
from olake.cli import app
from olake import __version__

runner = CliRunner()


def test_version_command():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    # Example output: "olake version: 0.1.0"
    assert "olake version:" in result.stdout
    assert __version__ in result.stdout


def test_help_lists_commands():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "OLake CLI" in result.stdout
    assert "version" in result.stdout
