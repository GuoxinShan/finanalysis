# src/finanalysis/cli.py
import click
import logging
from pathlib import Path
from . import __version__
from .config import Settings
from .pipeline import Pipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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

    click.echo(f"Parsing: {pdf_path}")
    click.echo(f"Output: {output_dir}")

    if force:
        click.echo("Cache: disabled (force=True)")

    if stage:
        click.echo(f"Running stage: {stage}")

    try:
        # Load settings from environment
        settings = Settings()

        # Create pipeline
        pipeline = Pipeline(settings=settings)

        # Run pipeline
        result = pipeline.run(
            pdf_path=pdf_path,
            output_dir=str(output_dir),
            force=force,
            stop_at_stage=stage
        )

        # Display results
        if result.get("status") == "stopped":
            click.echo(f"\n✓ Pipeline stopped at Stage {result['stage']}")
        else:
            click.echo("\n✓ Pipeline complete!")
            click.echo(f"  Pages: {result['statistics']['total_pages']}")
            click.echo(f"  Text blocks: {result['statistics']['text_blocks']}")
            click.echo(f"  Table rows: {result['statistics']['table_rows']}")
            click.echo(f"  Metrics: {result['statistics']['metrics']}")

            if result.get("extracted_metrics"):
                click.echo("\nExtracted Metrics:")
                for metric in result["extracted_metrics"]:
                    click.echo(f"  - {metric['type']}: {metric['value']} {metric.get('currency', '')} "
                              f"(confidence: {metric['confidence']:.0%})")

            if result.get("processing_notes"):
                click.echo("\nNotes:")
                for note in result["processing_notes"]:
                    click.echo(f"  - {note}")

            click.echo(f"\nOutput files saved to: {output_dir}")

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        logging.exception("Pipeline failed")
        raise click.Abort()

if __name__ == '__main__':
    cli()
