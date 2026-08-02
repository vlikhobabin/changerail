## 1. Series Refresh

- [x] 1.1 Rewrite `openspec/board/1.backlog/040-00-native-windows-implementation-epic.md`
  against the selected `030-03` architecture decision.
- [x] 1.2 Refresh `040-01-add-windows-runtime-entrypoints.md` with `.cmd`
  default runtime entrypoint acceptance and verification.
- [x] 1.3 Refresh `040-02-add-windows-wiring-backend.md` with generated-copy
  default wiring, explicit fallback and ownership semantics.
- [x] 1.4 Refresh `040-03-add-windows-verification-and-git-safety.md` with
  verifier, drift, Git and threat-model acceptance.
- [x] 1.5 Refresh `040-04-add-windows-automated-smoke.md` with deterministic
  local fixtures and two-host smoke matrix expectations.
- [x] 1.6 Refresh `040-05-prove-native-windows-end-to-end.md` with clean-clone
  lifecycle, final documentation and release-baseline expectations.

## 2. Verification

- [x] 2.1 Check cross-links and dependency order for every refreshed `040`
  card.
- [x] 2.2 Run `./bin/openspec validate refresh-native-windows-implementation-series --strict`.
- [x] 2.3 Run `./bin/openspec validate --all --strict`.
- [x] 2.4 Run `git diff --check`.
- [x] 2.5 Run `python3 scripts/public-surface-scan.py`.
