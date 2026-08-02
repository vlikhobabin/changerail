## 1. Architecture Decision

- [x] 1.1 Update `docs/compatibility.md` with the selected native Windows
  default path, bounded fallback table, prerequisites, ownership model,
  drift/upgrade/cleanup semantics, threat model and test matrix.
- [x] 1.2 Update `docs/wiring-discovery.md` so consumer wiring docs distinguish
  the existing POSIX symlink contract from the selected native Windows
  generated-copy architecture.
- [x] 1.3 Update the `030-03` card with ordered changes, architecture result,
  verification commands and archive handoff.

## 2. Verification

- [x] 2.1 Run architecture review against `030-01` and `030-02` tracked
  evidence in `docs/compatibility.md` and the archived dependency cards.
- [x] 2.2 Run `./bin/openspec validate freeze-native-windows-architecture --strict`.
- [x] 2.3 Run `./bin/openspec validate --all --strict`.
- [x] 2.4 Run `git diff --check`.
- [x] 2.5 Run `python3 scripts/public-surface-scan.py`.
