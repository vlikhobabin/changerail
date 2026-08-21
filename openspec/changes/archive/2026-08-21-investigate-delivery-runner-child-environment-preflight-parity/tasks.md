## 1. Investigation Decision

- [x] 1.1 Update the board card with the public-safe deterministic reproducer,
  execution-boundary inventory and selected child-equivalent preflight design.
- [x] 1.2 Record the structured terminal contract, retry taxonomy and
  consumer-scoped SSH override decision.
- [x] 1.3 Bind exact successor
  `add-delivery-runner-child-equivalent-preflight`, its current board path,
  production LOC ceiling 300, no-protocol-boundary declaration and required
  verification floor.
- [x] 1.4 Create the successor backlog card without implementing runner,
  launcher, schema, skill or smoke changes.

## 2. Spec Sync And Archive

- [x] 2.1 Sync the delta requirement into
  `openspec/specs/changerail-delivery-runner/spec.md`.
- [x] 2.2 Archive
  `investigate-delivery-runner-child-environment-preflight-parity` after
  validation succeeds.

## 3. Verification

- [x] 3.1 Run `./bin/openspec validate
  "investigate-delivery-runner-child-environment-preflight-parity" --strict`.
- [x] 3.2 Run `./bin/openspec validate "changerail-delivery-runner" --strict`.
- [x] 3.3 Run `./bin/openspec validate --all --strict`.
- [x] 3.4 Run `python3 scripts/public-surface-scan.py`.
- [x] 3.5 Run `git diff --check` and an explicit trailing-whitespace scan over
  untracked files.
