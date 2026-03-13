# src/finanalysis/cli.py
import click
from pathlib import Path
from . import __version__

@click.group()
@click.version_option(version=__version__, prog_name='finanalysis')
def cli():
    """Financial Report PDF Parsing Pipeline"""
    pass

@cli.command()
@click.argument('pdf_path', type=click.Path(exists=True))
@click.option('--out', '-o', default='./output', help='Output directory')
@click.option('--force', '-f', is_flag=True, help='Force reprocess (ignore cache)')
@click.option('--stage', '-s', type=int, help='Run specific stage only (1-5)')
def parse(pdf_path: str, out: str, force: bool, stage: int):
    """Parse a financial report PDF"""
    output_dir = Path(out)
    output_dir.mkdir(exist_ok=True, parents=True)

    click.echo(f"Parsing: {pdf_path}")
    click.echo(f"Output: {output_dir}")
    click.echo(f"Force: {force}")

    if stage:
        click.echo(f"Running stage: {stage}")

    # TODO: Implement pipeline execution
    click.echo("Pipeline not yet implemented")

if __name__ == '__main__':
    cli()
