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
@click.option('--company', '-c', default=None, help='Company name or stock code (e.g. CHINHIN, "Chin Hin Group Berhad")')
def parse(pdf_path: str, out: str, force: bool, stage: int, company: str):
    """Parse a financial report PDF"""
    output_dir = Path(out)

    click.echo(f"Parsing: {pdf_path}")
    click.echo(f"Output: {output_dir}")
    if company:
        click.echo(f"Company: {company}")

    if force:
        click.echo("Cache: disabled (force=True)")

    if stage:
        click.echo(f"Running stage: {stage}")

    try:
        settings = Settings()
        pipeline = Pipeline(settings=settings)

        result = pipeline.run(
            pdf_path=pdf_path,
            output_dir=str(output_dir),
            force=force,
            stop_at_stage=stage,
            company_name=company,
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


@cli.command()
@click.argument('label')
@click.option('--company', '-c', required=True, help='Company name or stock code (e.g. CHINHIN)')
@click.option('--year', '-y', type=int, required=True, help='Fiscal year (e.g. 2024)')
@click.option('--dirs', '-d', multiple=True, required=True, help='Pipeline output directories')
def query(label: str, company: str, year: int, dirs: tuple):
    """Query a financial metric by company and year.

    Example: finanalysis query revenue -c CHINHIN -y 2024 -d output/annual_2023 -d output/annual_2024
    """
    from .report_index import ReportIndex

    registry = ReportIndex()
    for d in dirs:
        registry.add(d)

    if company.upper() not in registry.companies():
        click.echo(f"Company '{company}' not found. Available: {registry.companies()}", err=True)
        raise click.Abort()

    result = registry.query(label, company=company, year=year)
    if result is None:
        click.echo(f"No data found for '{label}' ({company} FY{year})")
        return

    click.echo(f"\n{label.upper()} — {company} FY{year} ({result['currency']})")
    if result['group'] is not None:
        click.echo(f"  Group:   {result['group']:>15,.0f}")
    if result['company'] is not None:
        click.echo(f"  Company: {result['company']:>15,.0f}")


@cli.command('query-series')
@click.argument('label')
@click.option('--company', '-c', required=True, help='Company name or stock code')
@click.option('--dirs', '-d', multiple=True, required=True, help='Pipeline output directories')
@click.option('--entity', '-e', default='group', type=click.Choice(['group', 'company']), help='Entity level')
def query_series(label: str, company: str, dirs: tuple, entity: str):
    """Query a metric across all available years for a company.

    Example: finanalysis query-series revenue -c CHINHIN -d output/annual_2023 -d output/annual_2024
    """
    from .report_index import ReportIndex

    registry = ReportIndex()
    for d in dirs:
        registry.add(d)

    series = registry.query_series(label, company=company, entity=entity)
    if not series:
        click.echo(f"No data found for '{label}' ({company})")
        return

    currency = series[0]['currency'] if series else ''
    click.echo(f"\n{label.upper()} — {company} ({entity}) [{currency}]")
    click.echo(f"  {'Year':<6} {'Value':>15}")
    click.echo(f"  {'-'*6} {'-'*15}")
    for row in series:
        val = f"{row['value']:>15,.0f}" if row['value'] is not None else f"{'N/A':>15}"
        click.echo(f"  {row['year']:<6} {val}")



@click.option('--metric', '-m', default=None, help='Specific metric type to compare (e.g. revenue)')
def compare(output_dirs: tuple, metric: str):
    """Compare metrics across multiple parsed PDF output directories.

    Pass directories as: output/2023 output/2024 output/2025
    Labels are inferred from directory names.
    """
    from .compare import MetricComparer

    labeled = {Path(d).name: Path(d) for d in output_dirs}
    comparer = MetricComparer(output_dirs=labeled)

    if metric:
        rows = comparer.compare(metric_type=metric)
        if not rows:
            click.echo(f"No data found for metric: {metric}")
            return
        _print_comparison_table(metric, rows)
    else:
        all_results = comparer.compare_all()
        if not all_results:
            click.echo("No metrics found in provided directories.")
            return
        for mt, rows in all_results.items():
            if rows:
                _print_comparison_table(mt, rows)
                click.echo()


def _print_comparison_table(metric_type: str, rows: list):
    """Print a comparison table for a metric"""
    click.echo(f"\n{metric_type.upper().replace('_', ' ')}:")
    click.echo(f"  {'Year':<8} {'Value':>15} {'Currency':<8} {'YoY %':>8}  {'Conf':>6}")
    click.echo(f"  {'-'*8} {'-'*15} {'-'*8} {'-'*8}  {'-'*6}")
    for row in rows:
        value = f"{row['value']:,.0f}" if row['value'] is not None else "N/A"
        currency = row.get('currency') or ''
        yoy = f"{row['yoy_growth']:+.1f}%" if row.get('yoy_growth') is not None else "—"
        conf = f"{row['confidence']:.0%}" if row.get('confidence') is not None else "N/A"
        click.echo(f"  {row['label']:<8} {value:>15} {currency:<8} {yoy:>8}  {conf:>6}")


if __name__ == '__main__':
    cli()
