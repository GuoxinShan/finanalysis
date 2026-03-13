# tests/unit/test_cli.py
from click.testing import CliRunner
from src.finanalysis.cli import cli

def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert 'finanalysis' in result.output

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'parse' in result.output
