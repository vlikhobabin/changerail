## Context

`bin/changerail-delivery-metrics` already reads delivery run records and review
history, but its row model has only coarse usage and review findings. The new
runner performance contract gives metrics enough structured data to report slow
commands and review timing without reading raw logs.

## Goals / Non-Goals

**Goals:**
- Derive display `total_tokens` from input plus output tokens when explicit
  totals are absent.
- Render cached input, uncached input, output and reasoning token fields when
  available.
- Render slow-command summaries and review-cycle timing in text and CSV output.
- Keep missing optional fields visible as `unknown`.

**Non-Goals:**
- Do not mutate runtime status records while deriving metrics.
- Do not scrape raw `stdout.jsonl` or `stderr.log`.
- Do not replace review verdict validation with metrics heuristics.

## Decisions

- Build one normalized row per run, with helper functions that return
  user-facing strings and preserve `unknown` for unavailable optional data.
- Prefer status `performance.review` values when available, then augment with
  review-cycle history already read by the metrics helper.
- Keep CSV stable by adding explicit columns rather than embedding prose-only
  summaries.

## Risks / Trade-offs

- [Risk] CSV column growth can affect ad hoc consumers.
  Mitigation: append new columns after existing usage/review fields where
  possible and document the stable header in smoke coverage.
- [Risk] Derived token totals can be mistaken for provider-reported totals.
  Mitigation: derive only for display and leave runtime records unchanged.
- [Risk] Review timing is unavailable for old histories.
  Mitigation: render `unknown` instead of omitting the run.
