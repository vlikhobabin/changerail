## 1. Blocker and evidence contracts

- [ ] 1.1 Add RED contract fixtures for known/unknown blocker classes,
  value-free fields, secret-bearing rejection, evidence freshness and legacy
  retained recovery compatibility.
- [ ] 1.2 Extend delivery-run and plan-status schemas with external blocker,
  evidence policy and aggregate recovery metadata.
- [ ] 1.3 Add authoritative child terminal-event parsing that records the
  blocker only after schema/identity validation and captures canonical retained
  fingerprint.
- [ ] 1.4 When a project declares an execution target, retain only its logical
  id/fingerprint and reject blocker metadata that attempts provision, rebind or
  substitution authority.

## 2. Single-card resume

- [ ] 2.1 Add explicit evidence-index input and validate schema, source
  run/card scope, required ids, pass status, timestamps, redaction and maximum
  age before dirty-workspace authorization.
- [ ] 2.2 Reuse canonical `HEAD`/tree/diff fingerprint validation and add stable
  failure reasons for missing evidence, stale evidence, wrong scope, unknown
  blocker and payload drift.
- [ ] 2.3 Pass only value-free recovery context to the lifecycle child and prove
  the mandatory external gate and review/publish gates still run.
- [ ] 2.4 Preserve existing remote-preflight and `investigation_required`
  branches with explicit regression fixtures.
- [ ] 2.5 Reject missing/mismatched/multiple target evidence and target drift;
  prove explicit rebind requires a new clean attempt rather than dirty resume.

## 3. Queue resume

- [ ] 3.1 Persist bounded external retained recovery in aggregate card status
  and validate source child status before mirroring it.
- [ ] 3.2 Extend `resume-plan` to resume the original card, keep delivered cards
  skipped and release dependencies only after successful publish.
- [ ] 3.3 Add RED/GREEN fixtures for successful recovery, repeated blocker,
  abandoned recovery, mixed workspace, duplicate recovery and nonrecoverable
  blocker.
- [ ] 3.4 Add queue fixtures proving dependency release preserves the source
  target identity and cannot resume on a substituted target.

## 4. Documentation and verification

- [ ] 4.1 Document blocker taxonomy, evidence-index preparation, retry-only
  semantics and the prohibition on credential/output retention.
- [ ] 4.2 Run `python3 scripts/smoke-contract-schemas.py` and observe all new and
  legacy status fixtures pass.
- [ ] 4.3 Run `python3 scripts/smoke-delivery-runner.py` and observe single-card,
  plan, adversarial and investigation-resume fixtures pass.
- [ ] 4.4 Run `bin/openspec validate --all --strict`, `git diff --check` and
  `python3 scripts/public-surface-scan.py`; record outcomes without tracking
  runtime evidence.
