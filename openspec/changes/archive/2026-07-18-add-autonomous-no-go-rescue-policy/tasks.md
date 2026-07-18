## 1. Methodology And Skill Policy

- [x] 1.1 Update shared methodology docs to describe five-cycle autonomous
  same-card rescue, linked replacement cards, lineage guard and fail-closed
  publish semantics.
- [x] 1.2 Update `changerail-deliver` lifecycle instructions to remove manual
  exceptional authorization as the default autonomous path.
- [x] 1.3 Update user-facing workflow docs with autonomous recovery outcomes:
  replacement/rescue card, investigation/design card, `BLOCKED`,
  `SUPERSEDED` and `NOT-VERIFIABLE`.

## 2. Runner And Drift Contracts

- [x] 2.1 Update delivery runner contract docs/spec wording so aggregate
  `NO-GO` remains fail-fast and recovery resumes through a published linked
  card.
- [x] 2.2 Update smoke drift checks that look for the old two-cycle rescue
  contract.

## 3. Verification

- [x] 3.1 Run OpenSpec validation for the active change.
- [x] 3.2 Run focused smoke checks for wiring discovery and contract schemas.
- [x] 3.3 Run repository baseline checks for JSON/TOML parsing, whitespace,
  status and public-surface safety.
