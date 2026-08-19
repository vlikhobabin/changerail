## 1. Contract

- [ ] 1.1 Extend `schemas/changerail-delivery-run.schema.json` with optional `retained_payload` using `schema: changerail.retained-payload-identity.v1`.
- [ ] 1.2 Require retained identity fields for source run id, source status path, captured timestamp, card id/path, workspace root, `HEAD` commit, reviewed tree SHA, diff fingerprint and review target kind.
- [ ] 1.3 Add schema coverage that accepts a valid `investigation_required` retained-payload status and rejects raw source/log fields inside retained identity.

## 2. Runner Behavior

- [ ] 2.1 Reuse the canonical review fingerprint helper when a single-card delivery child exits `BLOCKED` with `terminal_reason: investigation_required`.
- [ ] 2.2 Populate `retained_payload` in the terminal status without copying raw source, raw child logs or ignored runtime evidence content.
- [ ] 2.3 Record a stable fail-closed diagnostic when retained-payload identity cannot be computed.

## 3. Verification

- [ ] 3.1 Add focused `scripts/smoke-delivery-runner.py` coverage for an `investigation_required` status with retained identity.
- [ ] 3.2 Run `./bin/openspec validate record-investigation-required-payload-identity --strict`.
- [ ] 3.3 Run `python3 scripts/smoke-delivery-runner.py`.
- [ ] 3.4 Run `git diff --check`.
- [ ] 3.5 Run `python3 scripts/public-surface-scan.py`.
