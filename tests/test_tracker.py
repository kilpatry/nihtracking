from pathlib import Path

import pytest

from nihtracking.tracker import plot_summary, summarize_by_fiscal_year


def test_summarize_by_fiscal_year():
    projects = [
        {"fy": 2020, "award_amount": 100000},
        {"fy": 2020, "award_amount": 250000.75},
        {"fy": 2021, "award_amount": 50000},
        {"fy": "2021", "award_amount": "25000"},
        {"fy": None, "award_amount": 10},
    ]

    summary = summarize_by_fiscal_year(projects)
    assert summary == {2020: 350000.75, 2021: 75000.0}


def test_plot_summary_creates_file(tmp_path: Path):
    pytest.importorskip("matplotlib")
    summary = {2019: 1000.0, 2020: 1500.5, 2021: 2000.25}

    output = tmp_path / "neonatal_plot.png"
    plot_summary(summary, output)

    assert output.exists()
    assert output.stat().st_size > 0


def test_plot_summary_rejects_empty_data(tmp_path: Path):
    pytest.importorskip("matplotlib")
    output = tmp_path / "empty_plot.png"
    with pytest.raises(ValueError):
        plot_summary({}, output)
