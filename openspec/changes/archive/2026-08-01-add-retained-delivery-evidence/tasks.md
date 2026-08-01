## 1. Contract And Helper

- [x] 1.1 Extend `changerail.evidence-index.v1` to model command evidence ids,
  command argv summaries, status, exit codes, timestamps, output paths,
  redaction state and evidence classification.
- [x] 1.2 Extend delivery manifest and review verdict schemas/helpers so
  verification summaries, acceptance entries and findings may reference retained
  evidence ids/paths without embedding raw logs.
- [x] 1.3 Implement `scripts/changerail_evidence.py` and
  `bin/changerail-evidence` through the shared ChangeRail Python runtime.
- [x] 1.4 Implement secret-like argv blocking, output redaction, timeout capture,
  index validation and missing-evidence diagnostics.

## 2. Integration And Documentation

- [x] 2.1 Update delivery/review manifest and verdict references to describe
  retained evidence handoff.
- [x] 2.2 Update public contract documentation and shared methodology wording
  for retained ignored runtime evidence.
- [x] 2.3 Add focused smoke coverage for success, failure, timeout, redaction and
  missing evidence, and wire it into the release baseline.

## 3. Verification

- [x] 3.1 Run `python3 scripts/smoke-retained-evidence.py`.
- [x] 3.2 Run manifest/verdict/schema smoke checks affected by the schema
  changes.
- [x] 3.3 Run `openspec validate add-retained-delivery-evidence --strict`,
  `openspec validate --all --strict`, `git diff --check`,
  `python3 scripts/public-surface-scan.py` and
  `python3 scripts/run-release-baseline.py`.
