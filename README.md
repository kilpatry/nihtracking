# Neonatal NIH Funding Tracker

This repository provides a small Python CLI for pulling NIH RePORTER data and summarizing funding for neonatal-related research across fiscal years.

## Quick start (running the CLI)

1) Use Python 3.11+ and, if desired, create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2) Install the only external dependency (matplotlib) if you want to generate plots. Everything else uses the standard library:
   ```bash
   pip install -r requirements.txt
   ```

3) Run the CLI to fetch neonatal-related projects and print a per-year funding summary (replace the years as needed):
   ```bash
   python -m nihtracking.cli --start-year 2018 --end-year 2023
   ```

   The command will call the NIH RePORTER API using the built-in neonatal text phrase ("neonatal OR neonate OR newborn OR NICU"), then print fiscal-year totals to stdout.

4) (Optional) Save outputs. Create the folders first (`mkdir -p summaries data plots`), then pass file paths to export data:
   ```bash
   # CSV of fiscal-year totals
   python -m nihtracking.cli --start-year 2018 --end-year 2023 --summary-output summaries/neonatal_funding.csv

   # Raw project JSON
   python -m nihtracking.cli --start-year 2020 --end-year 2023 --raw-output data/neonatal_projects.json

   # Funding-over-time plot (requires matplotlib)
   python -m nihtracking.cli --start-year 2018 --end-year 2023 --plot-output plots/neonatal_trend.png
   ```

5) For help at any time, run:
   ```bash
   python -m nihtracking.cli --help
   ```

### Notes about running

- The CLI contacts the live NIH RePORTER API, so you need network access. If you are behind a corporate proxy, set the standard `HTTP_PROXY`/`HTTPS_PROXY` environment variables before running.
- Award totals depend on the `award_amount` field reported by RePORTER; records missing this value are treated as zero for aggregation.
- Plotting requires matplotlib; if you only need CSV/JSON outputs you can skip installing it.

## How it works

- `nihtracking.client.NIHReporterClient` wraps the NIH RePORTER `projects/search` endpoint and paginates through the results.
- `nihtracking.tracker` summarizes award amounts by fiscal year, can export CSV/JSON output files, and can render a plot of funding over time.
- `nihtracking.cli` wires everything together for a simple command-line experience.

