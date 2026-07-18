## 1. Terminal Signal Contract

- [x] 1.1 Add backward-compatible `terminal_reason` fields to delivery-run and
  aggregate status schemas plus positive/negative contract fixtures.
- [x] 1.2 Parse exact terminal outcome/reason markers from completed
  agent-message events and preserve existing authoritative-event ordering.
- [x] 1.3 Fail closed with `unpublished_card` for unstructured exit `0` and with
  `missing_or_invalid_child_status` when queue child status is unavailable.

## 2. Recovery Plan Resume

- [x] 2.1 Add optional `recovery_for` plan/status fields and semantic validation
  for unique same-workspace, same-wave recovery cards with inherited
  dependencies.
- [x] 2.2 Accept fingerprint drift only for a constrained recovery augmentation
  of prior `NO-GO` or `fix_budget_exhausted` status.
- [x] 2.3 Keep source dependants blocked until recovery delivery passes normal
  publish-state checks, then record source `recovered` and `recovered_by`.

## 3. Evidence And Documentation

- [x] 3.1 Add runner smoke coverage for fix-budget marker parsing,
  unpublished exit `0`, invalid child status, external blocker and recovery
  insertion/order/failure.
- [x] 3.2 Update `docs/changerail-contracts.md` and runner methodology docs with
  terminal-reason and constrained recovery-plan examples.

## 4. Verification And Specs

- [x] 4.1 Run `python3 -m py_compile bin/changerail-delivery-runner` and
  `python3 scripts/smoke-delivery-runner.py`.
- [x] 4.2 Run `python3 scripts/smoke-contract-schemas.py`,
  `openspec validate enforce-fix-budget-terminal-and-recovery --strict`,
  `openspec validate --all --strict` and
  `python3 scripts/public-surface-scan.py`.
- [x] 4.3 Sync delta specs into main specs and archive the completed change.
