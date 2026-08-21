## 1. Identity contracts

- [ ] 1.1 Add RED schema fixtures for episode/attempt ids, attempt kinds,
  same-episode links, cross-episode rejection, duplicate conflicts and legacy
  optional-field compatibility.
- [ ] 1.2 Extend delivery-run, plan-status, review-history and manifest schemas
  with owner-scoped episode/attempt lineage.
- [ ] 1.3 Add `changerail.delivery-episode.v1` schema and include it in contract
  inventory/validation documentation.

## 2. Runtime lineage

- [ ] 2.1 Generate episode identity for first execution, reuse runner `run_id`
  as process attempt id and inherit validated episode/source links on resume.
- [ ] 2.2 Add unique linked review, rescue and publish attempt ids through their
  owner history/manifest writers.
- [ ] 2.3 Persist plan card episode identity and reject child or recovery links
  that cross card/workspace/episode boundaries.
- [ ] 2.4 Add an atomic idempotent episode refresh helper that merges only
  schema-valid owner summaries and reports conflicting duplicate attempts.

## 3. Complete bounded telemetry

- [ ] 3.1 Add RED fixtures proving command/tool aggregate counts and durations
  cover all observed events after detail samples truncate.
- [ ] 3.2 Record explicit observed/retained counts, limits and truncation for
  commands, tools and timeline samples.
- [ ] 3.3 Derive active, wait and operator-wait intervals only from structured
  transitions and mark unclosed intervals incomplete.
- [ ] 3.4 Add a value-free operator intervention event and adversarial fixture
  proving credentials, prompts, arguments/results and screenshots are absent.

## 4. Verification and docs

- [ ] 4.1 Document identity ownership, lineage semantics, legacy isolation,
  sampling limits and ignored episode storage.
- [ ] 4.2 Run `python3 scripts/smoke-contract-schemas.py` and observe new owner
  and episode contract fixtures pass.
- [ ] 4.3 Run `python3 scripts/smoke-delivery-runner.py` and observe one-pass,
  blocked/resumed, review-rescue, abandoned and truncated-run fixtures pass.
- [ ] 4.4 Run `bin/openspec validate --all --strict`, `git diff --check` and
  `python3 scripts/public-surface-scan.py`; retain raw results only under ignored
  runtime evidence.
