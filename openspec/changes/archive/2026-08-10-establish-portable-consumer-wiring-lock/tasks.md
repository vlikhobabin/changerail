## 1. Contract And Lock Generation

- [x] 1.1 Add `changerail.consumer-lock.v1` JSON Schema, examples and complete
  contract/verifier schema inventory.
- [x] 1.2 Implement public-safe clean-source version/revision resolution and
  advisory/strict lock rendering at the declared tracked path.
- [x] 1.3 Add semantic rejection for machine paths, credential-bearing sources,
  unsupported profiles and incomplete revisions.

## 2. POSIX Wiring And Repair

- [x] 2.1 Add absolute default and explicit relative POSIX symlink path modes to
  bootstrap/dry-run.
- [x] 2.2 Implement lock-owned POSIX refresh/repair with scope, parent-symlink,
  ownership and unrelated-dirty-state gates.
- [x] 2.3 Preserve native Windows generated-copy and fallback manifest behavior.

## 3. Verification And Discovery

- [x] 3.1 Add separate lock-schema, wiring-validity and source-drift checks to
  `verify-project` with advisory/strict severity.
- [x] 3.2 Extend wiring discovery JSON with lock/path-mode/source status while
  redacting resolved roots.
- [x] 3.3 Add non-sibling clean-clone regression plus broken-link, drift,
  project-owned and scope-escape negative fixtures.

## 4. Docs And Verification

- [x] 4.1 Update contracts, wiring, adoption, migration and compatibility docs.
- [x] 4.2 Run `python3 scripts/smoke-contract-schemas.py`, focused bootstrap,
  verify and wiring smoke and observe all new fixtures pass.
- [x] 4.3 Run `python3 scripts/smoke-windows-matrix.py --json` and confirm Windows
  backend compatibility remains green.
- [x] 4.4 Run `./bin/openspec validate --all --strict`, current/history
  public-surface scans and `git diff --check`.
