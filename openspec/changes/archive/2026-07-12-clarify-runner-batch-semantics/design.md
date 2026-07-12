## Context

`changerail-deliver` accepts a board column and processes cards one at a time.
The Python runner accepts one positional `card` and writes one status record.
Changing the runner into a full queue supervisor would require per-card status
records and new smoke coverage.

## Decision

Do not implement queue support in the runner in this change. Clarify the
current boundary instead:

- `$changerail-deliver` owns directory/queue interpretation.
- `bin/changerail-delivery-runner run <card>` owns non-interactive execution
  and structured status for a single card.

## Verification

- Update runner help/docstrings if needed.
- Run delivery runner smoke.
- Validate OpenSpec and run `git diff --check`.
