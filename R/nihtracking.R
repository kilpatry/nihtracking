# Neonatal NIH funding tracker implemented in R

API_URL <- "https://api.reporter.nih.gov/v2/projects/search"
DEFAULT_QUERY <- "neonatal OR neonate OR newborn OR NICU"
DEFAULT_FIELDS <- c(
  "project_num",
  "project_title",
  "pi_names",
  "org_name",
  "fy",
  "award_amount"
)

stop_for_missing_packages <- function(packages) {
  missing <- packages[!vapply(packages, requireNamespace, logical(1), quietly = TRUE)]
  if (length(missing) > 0) {
    stop(
      sprintf(
        "Install the following packages first: %s",
        paste(missing, collapse = ", ")
      ),
      call. = FALSE
    )
  }
}

search_projects <- function(query, years, limit = 500L, include_fields = DEFAULT_FIELDS) {
  stop_for_missing_packages(c("httr", "jsonlite"))

  if (limit > 500) {
    stop("NIH RePORTER only supports page sizes up to 500 records.")
  }

  years <- as.integer(years)
  if (length(years) == 0 || anyNA(years)) {
    stop("At least one valid fiscal year is required for the search.")
  }

  offset <- 0L
  all_results <- list()

  repeat {
    payload <- list(
      criteria = list(text_phrase = query, fiscal_years = years),
      include_fields = unname(include_fields),
      limit = limit,
      offset = offset
    )

    resp <- httr::POST(
      API_URL,
      body = payload,
      encode = "json",
      httr::content_type_json(),
      httr::accept_json(),
      httr::timeout(30)
    )

    if (httr::http_error(resp)) {
      detail <- tryCatch(
        httr::content(resp, as = "text", encoding = "UTF-8"),
        error = function(e) "<no response body>"
      )
      stop(
        sprintf("NIH RePORTER request failed: HTTP %s: %s", httr::status_code(resp), detail),
        call. = FALSE
      )
    }

    parsed <- httr::content(resp, as = "parsed", type = "application/json")
    page <- parsed$results

    if (is.null(page) || length(page) == 0) {
      break
    }

    all_results <- c(all_results, page)

    total <- parsed$meta$total
    offset <- offset + limit
    if (offset >= total) {
      break
    }
  }

  all_results
}

summarize_by_fiscal_year <- function(projects) {
  totals <- list()

  for (project in projects) {
    fiscal_year <- project$fy
    if (is.null(fiscal_year)) {
      next
    }

    amount <- project$award_amount
    if (is.null(amount)) {
      amount <- 0
    }

    suppressWarnings({
      fy <- as.integer(fiscal_year)
      amt <- as.numeric(amount)
    })

    if (is.na(fy) || is.na(amt)) {
      next
    }

    key <- as.character(fy)
    if (is.null(totals[[key]])) {
      totals[[key]] <- 0
    }

    totals[[key]] <- totals[[key]] + amt
  }

  if (length(totals) == 0) {
    return(list())
  }

  ordered_keys <- as.character(sort(as.integer(names(totals))))
  totals[ordered_keys]
}

write_summary_csv <- function(summary, path) {
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)

  fiscal_year <- names(summary)
  total_award_amount <- vapply(summary, function(x) sprintf("%.2f", x), character(1))
  data <- data.frame(fiscal_year = fiscal_year, total_award_amount = total_award_amount)
  utils::write.csv(data, file = path, row.names = FALSE)
}

write_raw_json <- function(projects, path) {
  stop_for_missing_packages("jsonlite")
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  jsonlite::write_json(projects, path, pretty = TRUE, auto_unbox = TRUE)
}

plot_summary <- function(summary, path) {
  if (length(summary) == 0) {
    stop("Summary is empty; nothing to plot.")
  }

  stop_for_missing_packages("ggplot2")

  years <- as.integer(names(summary))
  totals <- as.numeric(summary)
  plot_data <- data.frame(fiscal_year = years, total_award_amount = totals)

  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)

  p <- ggplot2::ggplot(plot_data, ggplot2::aes(x = fiscal_year, y = total_award_amount)) +
    ggplot2::geom_line(color = "steelblue") +
    ggplot2::geom_point(color = "steelblue", size = 2) +
    ggplot2::labs(
      title = "Neonatal NIH Funding by Fiscal Year",
      x = "Fiscal Year",
      y = "Total Award Amount (USD)"
    ) +
    ggplot2::theme_minimal()

  ggplot2::ggsave(filename = path, plot = p, width = 7, height = 4.5, dpi = 150)
}

collect_projects <- function(query, years) {
  all_projects <- list()
  distinct_years <- sort(unique(as.integer(years)))

  for (year in distinct_years) {
    year_results <- search_projects(query, year)
    all_projects <- c(all_projects, year_results)
  }

  all_projects
}

actionable_message <- function() {
  message(
    "Usage: Rscript R/neonatal_tracker.R --start-year <YEAR> --end-year <YEAR> [options]\n",
    "\n",
    "Options:\n",
    "  --start-year       First fiscal year to include (required)\n",
    "  --end-year         Last fiscal year to include (required)\n",
    "  --query            Override the default neonatal text phrase\n",
    "  --summary-output   CSV path for fiscal-year totals\n",
    "  --raw-output       JSON path for raw project data\n",
    "  --plot-output      Image path for funding-over-time plot (PNG recommended)\n",
    "  --help             Show this message\n"
  )
}

parse_args <- function(args) {
  if ("--help" %in% args || "-h" %in% args) {
    actionable_message()
    quit(status = 0)
  }

  parsed <- list()
  i <- 1
  while (i <= length(args)) {
    arg <- args[[i]]
    if (!startsWith(arg, "--")) {
      stop(sprintf("Unexpected argument: %s", arg))
    }

    if (i == length(args)) {
      stop(sprintf("Missing value for %s", arg))
    }

    value <- args[[i + 1]]
    name <- substring(arg, 3)
    parsed[[name]] <- value
    i <- i + 2
  }

  if (is.null(parsed[["start-year"]]) || is.null(parsed[["end-year"]])) {
    actionable_message()
    stop("--start-year and --end-year are required.")
  }

  parsed[["start-year"]] <- as.integer(parsed[["start-year"]])
  parsed[["end-year"]] <- as.integer(parsed[["end-year"]])
  if (is.na(parsed[["start-year"]]) || is.na(parsed[["end-year"]])) {
    stop("--start-year and --end-year must be valid integers.")
  }
  if (parsed[["start-year"]] > parsed[["end-year"]]) {
    stop("--start-year cannot be after --end-year.")
  }
  parsed[["query"]] <- parsed[["query"]] %||% DEFAULT_QUERY

  parsed
}

`%||%` <- function(lhs, rhs) {
  if (is.null(lhs)) rhs else lhs
}

run_cli <- function() {
  args <- parse_args(commandArgs(trailingOnly = TRUE))
  years <- seq(args[["start-year"]], args[["end-year"]])

  projects <- collect_projects(args$query, years)
  summary <- summarize_by_fiscal_year(projects)

  for (i in seq_along(summary)) {
    fy <- names(summary)[[i]]
    total <- summary[[i]]
    message(sprintf("FY %s: $%s", fy, format(round(total, 0), big.mark = ",", trim = TRUE)))
  }

  if (!is.null(args[["summary-output"]])) {
    write_summary_csv(summary, args[["summary-output"]])
    message(sprintf("Wrote summary CSV to %s", args[["summary-output"]]))
  }

  if (!is.null(args[["raw-output"]])) {
    write_raw_json(projects, args[["raw-output"]])
    message(sprintf("Wrote raw project data to %s", args[["raw-output"]]))
  }

  if (!is.null(args[["plot-output"]])) {
    plot_summary(summary, args[["plot-output"]])
    message(sprintf("Wrote plot to %s", args[["plot-output"]]))
  }
}
