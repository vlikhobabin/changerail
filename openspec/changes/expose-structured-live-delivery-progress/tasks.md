## 1. Progress contracts

- [ ] 1.1 Add RED schema fixtures for valid progress/health, unknown enums,
  content-bearing fields and running stale health in
  `scripts/smoke-contract-schemas.py`.
- [ ] 1.2 Extend delivery-run and plan-status schemas with the shared bounded
  progress and health definitions while preserving legacy v1 fixtures.

## 2. Single-card progress

- [ ] 2.1 Add a runner-owned ignored progress-event transport with run/card
  identity, schema and monotonic sequence validation.
- [ ] 2.2 Add coalesced heartbeat updates from valid Codex event envelopes and
  immediate updates for lifecycle transitions without storing event payload
  values.
- [ ] 2.3 Extend canonical lifecycle skills and wrappers to emit value-free
  `preflight -> ff -> do -> review -> publish` transitions and verify surface
  drift.
- [ ] 2.4 Add RED/GREEN runner fixtures for normal transitions, stale heartbeat,
  resumed child, terminated child and forged/secret-bearing events.

## 3. Aggregate status and diagnostics

- [ ] 3.1 Mirror only schema-valid matching child progress into plan card status
  and reject mismatched run/card identity.
- [ ] 3.2 Render bounded progress/health in single-card and plan text views while
  preserving JSON source records and existing terminal behavior.
- [ ] 3.3 Add deterministic stale diagnostics proving one missed interval does
  not terminate or reclassify a live process.

## 4. Documentation and verification

- [ ] 4.1 Update operator and contract documentation with interval, enum,
  transport, redaction and compatibility semantics.
- [ ] 4.2 Run `python3 scripts/smoke-contract-schemas.py` and observe all schema
  fixtures pass.
- [ ] 4.3 Run `python3 scripts/smoke-delivery-runner.py` and observe progress,
  resume, stalled and legacy runner fixtures pass.
- [ ] 4.4 Run `bin/openspec validate --all --strict`, `git diff --check` and
  `python3 scripts/public-surface-scan.py`; record command outcomes and retain
  raw outputs only in ignored runtime evidence.
