# Neonatal NIH Funding Tracker

This repository now includes both Python **and** R tooling for pulling NIH RePORTER data and summarizing neonatal-related funding by fiscal year.

## Quick start with R (new)

The R workflow mirrors the Python CLI but uses `httr`, `jsonlite`, and (optionally) `ggplot2` for plotting.

1) Install required R packages:

   ```bash
   R -q -e "install.packages(c('httr', 'jsonlite', 'ggplot2'), repos='https://cloud.r-project.org')"
   ```

2) Run the CLI (adjust years as needed):

   ```bash
   Rscript R/neonatal_tracker.R --start-year 2018 --end-year 2023
   ```

   By default the script uses the built-in neonatal text phrase ("neonatal OR neonate OR newborn OR NICU") and prints fiscal-year totals to stdout.

3) (Optional) Save outputs. Create output folders first (`mkdir -p summaries data plots`), then pass file paths:

   ```bash
   # CSV of fiscal-year totals
   Rscript R/neonatal_tracker.R --start-year 2018 --end-year 2023 --summary-output summaries/neonatal_funding.csv

   # Raw project JSON
   Rscript R/neonatal_tracker.R --start-year 2020 --end-year 2023 --raw-output data/neonatal_projects.json

   # Funding-over-time plot (requires ggplot2)
   Rscript R/neonatal_tracker.R --start-year 2018 --end-year 2023 --plot-output plots/neonatal_trend.png
   ```

4) For help at any time, run:

   ```bash
   Rscript R/neonatal_tracker.R --help
   ```

### Notes about running the R version

- The CLI contacts the live NIH RePORTER API, so you need network access and any required proxy configuration (`HTTP_PROXY`/`HTTPS_PROXY`).
- Award totals depend on the `award_amount` field reported by RePORTER; records missing this value are treated as zero during aggregation.
- Plotting requires `ggplot2`; if you only need CSV/JSON outputs you can omit it.
- Requests are split by fiscal year to avoid NIH RePORTER's pagination ceiling (offsets above 14,999 are rejected). If a single year's query still returns that many results, narrow the text phrase with more specific neonatal terms.

## Python version (still available)

The original Python CLI remains available for environments that prefer Python:

1) Use Python 3.11+ and, if desired, create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2) Install the optional plotting dependency:
   ```bash
   pip install -r requirements.txt
   ```

3) Run the CLI to fetch neonatal-related projects and print a per-year funding summary (replace the years as needed):
   ```bash
   python -m nihtracking.cli --start-year 2018 --end-year 2023
   ```

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

### Notes about running the Python version

- Network and proxy considerations mirror the R workflow.
- Award totals depend on the `award_amount` field reported by RePORTER; records missing this value are treated as zero for aggregation.
- Plotting requires matplotlib; if you only need CSV/JSON outputs you can skip installing it.

## How it works

- **R implementation**: `R/nihtracking.R` holds the NIH RePORTER client, fiscal-year aggregation, CSV/JSON export helpers, and optional plotting (via `ggplot2`). `R/neonatal_tracker.R` is the CLI entry point.
- **Python implementation**: `nihtracking.client.NIHReporterClient` wraps the NIH RePORTER `projects/search` endpoint and paginates through the results; `nihtracking.tracker` handles aggregation/exports/plotting; `nihtracking.cli` wires everything together for the CLI experience.
