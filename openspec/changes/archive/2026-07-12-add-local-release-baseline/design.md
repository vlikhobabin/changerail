## Context

Release docs currently list a minimum local baseline, while CI contains a longer
set of mandatory release checks. Operators need one command that reproduces the
mandatory CI baseline from the checkout so release verification does not depend
on manually copying commands from docs.

## Goals / Non-Goals

**Goals:**
- Provide one local command for the full mandatory release baseline.
- Keep the command public-safe by generating runtime fixtures under `.runtime/`.
- Reuse the same command inventory checked by `scripts/smoke-release-ci.py`.
- Document the command in release docs and README.

**Non-Goals:**
- Replace GitHub Actions as the release gate.
- Run private workspace drift inventory from the public baseline.
- Commit raw logs or runtime evidence from the local baseline.

## Decisions

- Add `scripts/run-release-baseline.py` as the local command. It runs each
  mandatory command with fail-fast semantics and prints the command/outcome
  summary.
- The script installs no dependencies itself; it expects the operator or CI step
  to install `requirements-dev.txt`. This keeps dependency setup explicit and
  reproducible.
- Drift coverage uses the same generated fixture as CI instead of operator
  inventory. Private inventory remains a separate release/operator check.
- CI invokes the local baseline after dependency setup so CI and local behavior
  share a single command list.

## Risks / Trade-offs

- A full local baseline can be slower than focused checks. Mitigation: keep it
  as release-facing verification and continue using focused commands during
  implementation.
- The command may produce ignored runtime files. Mitigation: use `.runtime/`
  and keep final status/public scan checks explicit.
