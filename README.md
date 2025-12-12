# Neonatal NIH Funding Tracker

This repository provides a small Python CLI for pulling NIH RePORTER data and summarizing funding for neonatal-related research across fiscal years.

## Quick start

1. Install requirements (matplotlib is used for plotting):
   ```bash
   pip install -r requirements.txt
   ```

2. Fetch neonatal-related projects and output a per-year funding summary:
   ```bash
   python -m nihtracking.cli --start-year 2018 --end-year 2023 --summary-output summaries/neonatal_funding.csv
   ```

   The script will query the NIH RePORTER API for projects containing common neonatal keywords ("neonatal", "neonate", "newborn", "NICU") and write a CSV with total award amounts by fiscal year.

3. Save the raw project data (optional):
   ```bash
   python -m nihtracking.cli --start-year 2020 --end-year 2023 --raw-output data/neonatal_projects.json
   ```

4. Generate a funding-over-time plot (optional):
   ```bash
   python -m nihtracking.cli --start-year 2018 --end-year 2023 --plot-output plots/neonatal_trend.png
   ```
   The plot shows a line chart of neonatal NIH funding totals per fiscal year.

## How it works

- `nihtracking.client.NIHReporterClient` wraps the NIH RePORTER `projects/search` endpoint and paginates through the results.
- `nihtracking.tracker` summarizes award amounts by fiscal year, can export CSV/JSON output files, and can render a plot of funding over time.
- `nihtracking.cli` wires everything together for a simple command-line experience.

## Notes

- Network access is required to contact the NIH API.
- Award totals depend on the `award_amount` field reported by RePORTER; records missing this value are treated as zero for aggregation.

