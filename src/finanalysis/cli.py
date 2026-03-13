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

@cli.command()
@click.argument('output_dir', type=click.Path(exists=True))
@click.argument('query')
@click.option('--top-k', '-k', default=10, help='Number of results to return')
@click.option('--source', type=click.Choice(['all', 'text', 'table']), default='all', help='Source to search')
def search(output_dir: str, query: str, top_k: int, source: str):
    """Search extracted chunks from a parsed PDF output directory"""
    from .retrieval import ChunkRetriever

    retriever = ChunkRetriever(output_dir=Path(output_dir))
    results = retriever.search(query=query, top_k=top_k)

    # Filter by source if specified
    if source != 'all':
        results = [r for r in results if r['source'] == source]

    if not results:
        click.echo(f"No results found for: {query}")
        return

    click.echo(f"\nFound {len(results)} results for '{query}':\n")
    for i, r in enumerate(results, 1):
        click.echo(f"[{i}] Page {r['page_number']} ({r['source']}) — score: {r['score']:.2f}")
        click.echo(f"    {r['text'][:200]}")
        click.echo()


if __name__ == '__main__':
    cli()
