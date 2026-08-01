## 1. Runtime Contract And Selector

- [x] 1.1 Add explicit runtime dependency source for ChangeRail Python helpers.
- [x] 1.2 Implement the shared `bin/changerail-python` selector with
  `CHANGERAIL_PYTHON` override, version/module probe, ignored runtime record
  and actionable diagnostics.
- [x] 1.3 Route `bin/bootstrap-project`, `bin/verify-project`,
  `bin/changerail-review-verdict`, `bin/changerail-delivery-runner` and
  `bin/changerail-delivery-metrics` through the shared selector without
  changing their public command names.
- [x] 1.4 Route delivery manifest and review verdict helper invocations in
  docs/skills through the same selector where they are runtime entrypoints.

## 2. Docs And Migration

- [x] 2.1 Update `docs/compatibility.md` with Python 3.11 minimum,
  runtime modules/packages, install command and `CHANGERAIL_PYTHON` override.
- [x] 2.2 Update `docs/migration-guide.md` with unreleased runtime remediation
  notes for operators and consumer projects.
- [x] 2.3 Keep runtime state examples under ignored `.runtime/changerail/`
  paths and avoid publishing local interpreter paths as tracked evidence.

## 3. Smoke And Release Baseline

- [x] 3.1 Add focused runtime smoke covering supported runtime selection,
  old-version simulation, missing dependency simulation and invalid override.
- [x] 3.2 Add the runtime smoke to `scripts/run-release-baseline.py` and the
  CI contract smoke inventory when required.
- [x] 3.3 Verify changed helper entrypoints still compile as Python after the
  polyglot prelude.

## 4. Verification

- [x] 4.1 Run focused runtime smoke.
- [x] 4.2 Run `python3 scripts/run-release-baseline.py` from a supported
  environment.
- [x] 4.3 Run `./bin/openspec validate --all --strict`.
- [x] 4.4 Run `python3 scripts/public-surface-scan.py`.
- [x] 4.5 Run `git diff --check`.
