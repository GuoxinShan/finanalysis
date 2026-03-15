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
@click.argument('dirs', nargs=-1, required=True)
@click.option('--registry', '-r', default='output/registry.json', help='Registry file path')
def register(dirs: tuple, registry: str):
    """Register pipeline output directories into a persistent registry.

    Example: finanalysis register output/CHINHIN/2023 output/CHINHIN/2024
    """
    from .report_index import ReportIndex

    reg = ReportIndex.load(registry) if Path(registry).exists() else ReportIndex()
    for d in dirs:
        reg.add(d)
    reg.save(registry)
    click.echo(f"Registry saved to {registry}")
    click.echo(f"Companies: {reg.companies()}")
    for c in reg.companies():
        click.echo(f"  {c}: {reg.years(c)}")


@cli.command('list')
@click.option('--registry', '-r', default='output/registry.json', help='Registry file path')
def list_registry(registry: str):
    """List all companies and years in the registry."""
    from .report_index import ReportIndex

    reg = ReportIndex.load(registry)
    if not reg.companies():
        click.echo(f"Registry is empty or not found at {registry}")
        click.echo("Run: finanalysis register <output_dirs>")
        return

    click.echo(f"\nRegistry: {registry}")
    for company in reg.companies():
        years = reg.years(company)
        for year in years:
            idx = reg.get_index(company, year)
            fy = idx.fiscal_year_end if idx else "?"
            items = len(idx.line_items) if idx else 0
            currency = idx.currency if idx else "?"
            click.echo(f"  {company:<12} FY{year}  {fy}  {items:>3} items  {currency}")


@cli.command()
@click.argument('label')
@click.option('--company', '-c', required=True, help='Company name or stock code (e.g. CHINHIN)')
@click.option('--year', '-y', type=int, required=True, help='Fiscal year (e.g. 2024)')
@click.option('--dirs', '-d', multiple=True, help='Pipeline output directories (or use --registry)')
@click.option('--registry', '-r', default='output/registry.json', help='Registry file path')
def query(label: str, company: str, year: int, dirs: tuple, registry: str):
    """Query a financial metric by company and year.

    Uses saved registry by default, or pass -d dirs directly.

    Example: finanalysis query revenue -c CHINHIN -y 2024
    """
    from .report_index import ReportIndex

    if dirs:
        reg = ReportIndex().add_many(dirs)
    else:
        reg = ReportIndex.load(registry)
        if not reg.companies():
            click.echo(f"No registry found at {registry}. Run 'finanalysis register <dirs>' first, or pass -d dirs.", err=True)
            raise click.Abort()

    if company.upper() not in reg.companies():
        click.echo(f"Company '{company}' not found. Available: {reg.companies()}", err=True)
        raise click.Abort()

    result = reg.query(label, company=company, year=year)
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
@click.option('--dirs', '-d', multiple=True, help='Pipeline output directories (or use --registry)')
@click.option('--registry', '-r', default='output/registry.json', help='Registry file path')
@click.option('--entity', '-e', default='group', type=click.Choice(['group', 'company']), help='Entity level')
def query_series(label: str, company: str, dirs: tuple, registry: str, entity: str):
    """Query a metric across all available years for a company.

    Example: finanalysis query-series revenue -c CHINHIN
    """
    from .report_index import ReportIndex

    if dirs:
        reg = ReportIndex().add_many(dirs)
    else:
        reg = ReportIndex.load(registry)
        if not reg.companies():
            click.echo(f"No registry found at {registry}. Run 'finanalysis register <dirs>' first, or pass -d dirs.", err=True)
            raise click.Abort()

    series = reg.query_series(label, company=company, entity=entity)
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


@cli.command()
@click.argument('output_dirs', nargs=-1, required=True)
@click.option('--metric', '-m', default=None, help='Specific metric type to compare (e.g. revenue)')
def compare(output_dirs: tuple, metric: str):
    """Compare metrics across multiple parsed PDF output directories.

    Pass directories as: output/2023 output/2024 output/2025
    Labels use FY year from fs_index if available, else directory name.
    """
    from .compare import MetricComparer
    from .fs_index import FSIndex

    # Build labels: prefer FY year from fs_index
    labeled = {}
    for d in output_dirs:
        p = Path(d)
        fs_path = p / "fs_index.json"
        label = p.name
        if fs_path.exists():
            idx = FSIndex.load(fs_path)
            if idx.fiscal_year_end:
                label = f"FY{idx.fiscal_year_end[:4]}"
        labeled[label] = p

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


@cli.command()
@click.argument('fs_index_path', type=click.Path(exists=True))
@click.option('--prior', '-p', type=click.Path(exists=True), help='Prior year fs_index.json')
@click.option('--output', '-o', default=None, help='Output JSON file')
def calculate(fs_index_path: str, prior: str, output: str):
    """Calculate derived financial metrics from fs_index.json

    Example:
        finanalysis calculate output/CHINHIN/2024/fs_index.json \\
            --prior output/CHINHIN/2023/fs_index.json \\
            --output output/CHINHIN/2024/metrics.json
    """
    import json
    from .fs_index import FSIndex
    from .calculators.metrics import MetricsCalculator

    fs_index = FSIndex.load(Path(fs_index_path))
    prior_fs_index = FSIndex.load(Path(prior)) if prior else None

    calculator = MetricsCalculator(fs_index, prior_fs_index)
    output_data = calculator.to_output_dict(fs_index_path)

    if output:
        with open(output, 'w') as f:
            json.dump(output_data, f, indent=2)
        click.echo(f"✓ Metrics saved to {output}")
    else:
        click.echo(json.dumps(output_data, indent=2))


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


@cli.command()
@click.argument('fs_index_path', type=click.Path(exists=True))
@click.option('--entity', '-e', default='group', type=click.Choice(['group', 'company']),
              help='Entity to validate')
@click.option('--period', '-p', default='current', type=click.Choice(['current', 'prior']),
              help='Period to validate')
@click.option('--tolerance', '-t', default=1.0, type=float,
              help='Acceptable difference for floating point comparisons')
def validate(fs_index_path: str, entity: str, period: str, tolerance: float):
    """Validate balance sheet equations for mathematical accuracy.

    Checks:
    - Total Assets = Non-Current Assets + Current Assets
    - Total Assets = Total Liabilities + Total Equity
    - Total Equity = Share Capital + Reserves + Retained Earnings

    Example:
        finanalysis validate output/CHINHIN/2024/fs_index.json --entity group --period current
    """
    import json
    from .fs_index import FSIndex
    from .validation import BalanceSheetValidator, format_validation_report

    fs_index = FSIndex.load(Path(fs_index_path))

    # Convert FSIndex to metrics dict format
    metrics = {}
    for key, entry in fs_index.line_items.items():
        if '(' in key:  # Skip parentheses variants
            continue
        metrics[key] = {
            'group_current': entry.get('group_current'),
            'group_prior': entry.get('group_prior'),
            'company_current': entry.get('company_current'),
            'company_prior': entry.get('company_prior'),
        }

    # Run validation
    validator = BalanceSheetValidator(tolerance=tolerance)
    issues = validator.validate(metrics, entity=entity, period=period)

    # Print report
    report = format_validation_report(issues)
    click.echo(report)

    # Print metadata
    click.echo(f"\nCompany: {fs_index.company_name}")
    click.echo(f"Fiscal Year End: {fs_index.fiscal_year_end}")
    click.echo(f"Currency: {fs_index.currency}")
    click.echo(f"Entity: {entity}")
    click.echo(f"Period: {period}")

    # Exit with error code if critical issues found
    critical_issues = [i for i in issues if i.severity == "error"]
    if critical_issues:
        raise click.Abort()


@cli.command('validate-report')
@click.argument('report', type=click.Path(exists=True))
@click.option('--data', type=click.Path(exists=True), required=True,
              help='Path to fs_index.json (source data)')
@click.option('--metrics', type=click.Path(exists=True),
              help='Path to metrics.json (calculated ratios)')
@click.pass_context
def validate_report_cmd(ctx, report, data, metrics):
    """Validate financial analysis report for data accuracy.

    Checks:
    - Numbers match source data (fs_index.json)
    - Calculations are correct (YoY %, margins)
    - Metrics are consistent across sections
    - Units are correct

    Exit codes:
        0 = All checks passed
        1 = Critical data accuracy issues found
    """
    import subprocess
    import sys

    # Find skill directory (relative to this file)
    cli_dir = Path(__file__).parent
    skill_dir = cli_dir.parent.parent / 'skills' / 'financial-analysis-report'
    validate_script = skill_dir / 'scripts' / 'validate_report.py'

    if not validate_script.exists():
        click.echo(f"Error: Validation script not found at {validate_script}", err=True)
        click.echo("Make sure the financial-analysis-report skill is installed.", err=True)
        ctx.exit(1)

    # Build command
    cmd = [sys.executable, str(validate_script), report, '--data', data]
    if metrics:
        cmd.extend(['--metrics', metrics])

    # Run validation (forward exit code)
    result = subprocess.run(cmd)
    ctx.exit(result.returncode)


if __name__ == '__main__':
    cli()
