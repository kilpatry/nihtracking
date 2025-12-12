"""Aggregation and visualization utilities for NIH neonatal funding."""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Mapping


def summarize_by_fiscal_year(projects: Iterable[Mapping[str, object]]) -> dict[int, float]:
    """Aggregate total award amounts by fiscal year."""
    totals: dict[int, float] = defaultdict(float)
    for project in projects:
        fiscal_year = project.get("fy")
        if fiscal_year is None:
            continue

        amount = project.get("award_amount") or 0
        try:
            fy_int = int(fiscal_year)
            amount_float = float(amount)
        except (TypeError, ValueError):
            continue

        totals[fy_int] += amount_float

    return dict(sorted(totals.items()))


def write_summary_csv(summary: Mapping[int, float], path: str | Path) -> None:
    """Write fiscal-year totals to a CSV file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["fiscal_year", "total_award_amount"])
        for fy, total in summary.items():
            writer.writerow([fy, f"{total:.2f}"])


def write_raw_json(projects: Iterable[Mapping[str, object]], path: str | Path) -> None:
    """Write raw project data to JSON for later inspection."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w") as handle:
        json.dump(list(projects), handle, indent=2)


def plot_summary(summary: Mapping[int, float], path: str | Path) -> None:
    """Render a line chart of award totals over time.

    Args:
        summary: Mapping of fiscal year to total award amount.
        path: Output image file path (PNG recommended).
    """

    if not summary:
        raise ValueError("Summary is empty; nothing to plot.")

    # Local import to keep matplotlib optional for environments where it is unavailable
    import matplotlib
    from matplotlib import pyplot as plt

    matplotlib.use("Agg")

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    years = sorted(summary)
    totals = [summary[year] for year in years]

    fig, ax = plt.subplots()
    ax.plot(years, totals, marker="o")
    ax.set_xlabel("Fiscal Year")
    ax.set_ylabel("Total Award Amount (USD)")
    ax.set_title("Neonatal NIH Funding by Fiscal Year")
    ax.grid(True, linestyle="--", alpha=0.5)

    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
