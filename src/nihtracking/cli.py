"""Command-line interface for neonatal NIH funding tracking."""
from __future__ import annotations

import argparse
from typing import Iterable, Mapping

from .client import NIHReporterClient, SearchCriteria
from .tracker import (
    plot_summary,
    summarize_by_fiscal_year,
    write_raw_json,
    write_summary_csv,
)


DEFAULT_QUERY = "neonatal OR neonate OR newborn OR NICU"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--start-year", type=int, required=True, help="First fiscal year to include"
    )
    parser.add_argument(
        "--end-year", type=int, required=True, help="Last fiscal year to include"
    )
    parser.add_argument(
        "--query",
        default=DEFAULT_QUERY,
        help="Text phrase for NIH RePORTER search (defaults to neonatal keywords)",
    )
    parser.add_argument(
        "--summary-output",
        default=None,
        help="Optional CSV path for fiscal-year totals",
    )
    parser.add_argument(
        "--raw-output",
        default=None,
        help="Optional JSON path for raw project data",
    )
    parser.add_argument(
        "--plot-output",
        default=None,
        help="Optional image path for a funding-over-time plot (PNG recommended)",
    )
    return parser.parse_args()


def collect_projects(query: str, years: Iterable[int]) -> list[Mapping[str, object]]:
    client = NIHReporterClient()
    criteria = SearchCriteria(text_phrase=query, fiscal_years=years)
    return client.search_projects(criteria)


def main() -> None:
    args = parse_args()
    years = range(args.start_year, args.end_year + 1)

    projects = collect_projects(args.query, years)
    summary = summarize_by_fiscal_year(projects)

    for fy, total in summary.items():
        print(f"FY {fy}: ${total:,.0f}")

    if args.summary_output:
        write_summary_csv(summary, args.summary_output)
        print(f"Wrote summary CSV to {args.summary_output}")

    if args.raw_output:
        write_raw_json(projects, args.raw_output)
        print(f"Wrote raw project data to {args.raw_output}")

    if args.plot_output:
        plot_summary(summary, args.plot_output)
        print(f"Wrote plot to {args.plot_output}")


if __name__ == "__main__":
    main()
