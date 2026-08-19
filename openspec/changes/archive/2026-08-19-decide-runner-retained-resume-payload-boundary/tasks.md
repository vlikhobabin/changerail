## 1. Investigation Decision

- [x] 1.1 Update the board card with the public-safe retained preflight
  breakdown: 562 production-counted LOC in `bin/changerail-delivery-runner`,
  new runner/status protocol boundary and no published authorization.
- [x] 1.2 Record the bounded successor decision: exact successor
  `support-runner-resume-after-investigation-required`, simplified successor
  ceiling 500 and later authorization protocol allowance true.
- [x] 1.3 Preserve the retained-resume verification floor and state that the
  retained payload is investigation input only, not review or publish evidence.

## 2. Spec Sync And Archive

- [x] 2.1 Sync the delta requirement into
  `openspec/specs/changerail-contracts/spec.md`.
- [x] 2.2 Archive
  `decide-runner-retained-resume-payload-boundary` after validation succeeds.

## 3. Verification

- [x] 3.1 Run `./bin/openspec validate "decide-runner-retained-resume-payload-boundary" --strict`.
- [x] 3.2 Run `./bin/openspec validate "changerail-contracts" --strict`.
- [x] 3.3 Run `./bin/openspec validate --all --strict`.
- [x] 3.4 Run `python3 scripts/public-surface-scan.py`.
- [x] 3.5 Run `git diff --check`.
