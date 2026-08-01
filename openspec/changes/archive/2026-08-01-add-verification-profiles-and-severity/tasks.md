## 1. Verification Contract

- [x] 1.1 Normalize `bin/verify-project` results to include stable `status`,
  `severity` and `message` fields in JSON output.
- [x] 1.2 Derive summary status as `pass`, `pass-with-diagnostics` or `fail`
  with exit `0` only for non-failing summaries.
- [x] 1.3 Parse tracked verification profile policy from
  `openspec/config.yaml`, fail closed on malformed policy and preserve strict
  all-surfaces behavior when no override is present.
- [x] 1.4 Enforce `required`, `optional` and `forbidden` surface states for
  Codex, Claude and legacy MCP surfaces.
- [x] 1.5 Keep targeted card-owned OpenSpec validation mandatory and reject
  policy attempts to weaken it.
- [x] 1.6 Allow project-wide baseline debt as a non-blocking diagnostic only
  when tracked policy records command, residual risk and non-card-owned
  rationale.

## 2. Templates And Guidance

- [x] 2.1 Update `templates/project/openspec/config.yaml.tpl` with the strict
  default verification profile policy.
- [x] 2.2 Update generated project guidance so consumers understand
  `required`, `optional`, `forbidden`, `pass-with-diagnostics` and the
  mandatory targeted validation boundary.

## 3. Smoke Coverage

- [x] 3.1 Extend `scripts/smoke-verify-project.py` with a Codex-only fixture
  that passes with non-blocking Claude diagnostics.
- [x] 3.2 Extend smoke coverage for the default all-surfaces profile to fail on
  missing canonical surfaces.
- [x] 3.3 Extend smoke coverage for forbidden legacy artifacts.
- [x] 3.4 Extend smoke coverage for attempts to weaken mandatory targeted
  validation.
- [x] 3.5 Keep generated bootstrap/verify smoke coverage green with the new
  default policy.

## 4. Specs And Verification

- [x] 4.1 Sync delta specs into main specs after implementation.
- [x] 4.2 Run `./bin/openspec validate add-verification-profiles-and-severity
  --strict`.
- [x] 4.3 Run focused `python3 scripts/smoke-verify-project.py`.
- [x] 4.4 Run generated project bootstrap smoke and release baseline:
  `python3 scripts/smoke-bootstrap-project.py` and
  `python3 scripts/run-release-baseline.py`.
- [x] 4.5 Run public-surface scans:
  `python3 scripts/public-surface-scan.py` and
  `python3 scripts/public-surface-scan.py --history`.
- [x] 4.6 Run `git diff --check`.
