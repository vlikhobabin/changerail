## 1. Planning integration

- [x] 1.1 Add RED fixtures where a configured rule is omitted from an otherwise
  complete OpenSpec plan and where card acceptance changes after plan creation.
- [x] 1.2 Extend canonical `changerail-ff` to validate the map and write one
  fingerprint-bound `verification-coverage.json` per change.
- [x] 1.3 Update lifecycle wrappers/generated guidance and run drift checks for
  canonical/alias skill surfaces.

## 2. Delivery reconciliation

- [x] 2.1 Implement deterministic matcher for manifest path operations and
  schema-valid namespaced extension surfaces.
- [x] 2.2 Block on actual applicable ids absent from planning; retain planned
  non-applicable ids with explicit scope evidence.
- [x] 2.3 Link required observed evidence-index entries into ignored ledger and
  add bounded coverage summary to delivery manifest.
- [x] 2.4 Extend `changerail-do` to refresh ledger after verification and before
  review handoff without embedding raw outputs.

## 3. Review enforcement

- [x] 3.1 Extend deterministic review preflight to validate map/plan/card/scope/
  review fingerprints and missing/stale/invalid evidence before model launch.
- [x] 3.2 Extend independent review skill to audit each applicable invariant,
  published boundary and test adequacy while keeping verdict authority.
- [x] 3.3 Add RED/GREEN generic Python fixtures for missing positive route,
  internal-only timeout assertion and disconnected producer/renderer proof.
- [x] 3.4 Add no-map compatibility and configured-map scope-drift fixtures.

## 4. Documentation and verification

- [x] 4.1 Update shared methodology, skill references and consumer guidance for
  planning, evidence, deterministic preflight and independent review ownership.
- [x] 4.2 Run `python3 scripts/smoke-review-preflight.py`,
  `python3 scripts/smoke-verify-project.py` and relevant lifecycle skill smokes;
  observe all false-green and compatibility cases pass.
- [x] 4.3 Run `python3 scripts/smoke-contract-schemas.py` and observe manifest,
  ledger and evidence references validate.
- [x] 4.4 Run `bin/openspec validate --all --strict`, `git diff --check`,
  `python3 scripts/smoke-drift.py` and `python3 scripts/public-surface-scan.py`;
  retain command output only in ignored evidence.
