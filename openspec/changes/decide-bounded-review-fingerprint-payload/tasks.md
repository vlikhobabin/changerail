## 1. Investigation Decision

- [ ] 1.1 Update the investigation card with the retained public-safe 527
  production-LOC breakdown.
- [ ] 1.2 Record the concrete simplification boundary: consolidate timing/cache
  helper code, avoid unnecessary dataclass layers and compact repeated smoke
  fixture setup without weakening verification.
- [ ] 1.3 State that the retained local checkpoint is read-only investigation
  evidence and MUST NOT be published or treated as independent review evidence.

## 2. Successor Handoff

- [ ] 2.1 Bind the decision to exact successor card
  `deliver-bounded-review-fingerprint-optimization`.
- [ ] 2.2 State the replacement ceiling as at most 500 added production LOC,
  with no global limit increase and no new authority or wire protocol.
- [ ] 2.3 Confirm the successor verification floor preserves exact tree parity,
  untracked hashing, cache invalidation, diagnostics and synthetic benchmark
  coverage.

## 3. Verification

- [ ] 3.1 Run `./bin/openspec validate "decide-bounded-review-fingerprint-payload" --strict`.
- [ ] 3.2 Run `./bin/openspec validate --all --strict`.
- [ ] 3.3 Run `python3 scripts/public-surface-scan.py`.
- [ ] 3.4 Run `git diff --check`.
