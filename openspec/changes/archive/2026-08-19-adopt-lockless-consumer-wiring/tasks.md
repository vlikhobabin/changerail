## 1. Adoption Planning Surface

- [x] 1.1 Add an explicit lockless adoption flag under
  `bin/bootstrap-project --configure-existing` and keep plain
  `--refresh-wiring` fail-closed when the consumer lock is missing.
- [x] 1.2 Build an inventory-first adoption plan from the canonical wiring
  inventory with keep/add/reject decisions for allowlisted commands, skills and
  helper wrappers.
- [x] 1.3 Make dry-run print backend, path mode, source evidence and all
  keep/add/reject decisions without creating lock, manifest or helper files.

## 2. Ownership And Mutation Gates

- [x] 2.1 Implement POSIX single-root symlink ownership and absolute/relative
  path-mode inference for accepted lockless wiring.
- [x] 2.2 Implement Windows generated-copy and fallback proof checks that block
  adoption when ownership metadata or proof is missing.
- [x] 2.3 Block dangling, mixed-root, mixed-mode, regular-file, project-owned,
  undeclared, scope-escaping and unrelated-dirty-state conflicts before
  mutation.
- [x] 2.4 Add scoped rollback that removes only artifacts created by the current
  adoption run and never recurses into link targets.

## 3. Lock, Manifest And Verification

- [x] 3.1 Generate schema-valid `openspec/changerail-consumer-lock.json` only
  after full adoption preflight passes and ChangeRail source revision is clean.
- [x] 3.2 Add missing newly supported helpers through the inferred owned
  backend/path mode and record them in lock or generated ownership metadata.
- [x] 3.3 Update `bin/verify-project` diagnostics to distinguish lockless
  compatibility, adoptable lockless consumers, unsafe adoption and adopted
  lock-backed refresh remediation.
- [x] 3.4 Add smoke fixtures for successful legacy adoption, mixed roots,
  missing helper addition, dirty unrelated file, regular-file conflict,
  unsupported Windows inference and idempotent second run.

## 4. Docs And Verification

- [x] 4.1 Update `docs/consumer-adoption-runbook.md` and generated guidance with
  lockless migration, dry-run, apply, verification and rollback steps.
- [x] 4.2 Run `./bin/openspec validate adopt-lockless-consumer-wiring --strict`.
- [x] 4.3 Run focused bootstrap and verify smoke commands covering the new
  adoption fixtures.
- [x] 4.4 Run `./bin/openspec validate --all --strict`, `git diff --check` and
  `python3 scripts/public-surface-scan.py`.
