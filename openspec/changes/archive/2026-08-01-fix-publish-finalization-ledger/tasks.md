## 1. Implementation

- [x] 1.1 Update delivery manifest schema/helper so `publish.payload_commit` and
  `publish.published_commit` are distinct, final remote/branch/status/timestamp
  are recorded, and legacy ambiguous `commit` is no longer the primary new
  ledger field.
- [x] 1.2 Update `finalize-card` so tracked card text contains stable final
  outcome only, does not include its own exact final commit hash or mutable push
  state, and does not introduce EOF whitespace defects.
- [x] 1.3 Update `finalize-card` or the publish flow so the ignored manifest
  records final `card.path` and `card.status` after the board move.
- [x] 1.4 Update `changerail-pub` contract/reference docs and methodology docs
  so exact commit/push ledger data belongs in the ignored manifest, while the
  tracked card records stable completion state.

## 2. Verification

- [x] 2.1 Add or update manifest schema/helper smoke coverage for
  `payload_commit`, `published_commit`, final card path/status and invalid
  publish ledger fields.
- [x] 2.2 Add a focused local bare-remote regression smoke that performs payload
  commit, card finalization, amend, push and manifest publish-update, then
  verifies tracked card text has no exact final commit hash and no pending push
  state.
- [x] 2.3 Run focused publish finalization smoke, manifest schema smoke,
  `git show --check --oneline HEAD` in the fixture, `./bin/openspec validate
  --all --strict`, `git diff --check`, public-surface scan and release
  baseline.

## 3. OpenSpec

- [x] 3.1 Sync delta specs into main specs after implementation verification.
- [x] 3.2 Archive `fix-publish-finalization-ledger` and record archive/evidence
  in the card and manifest.

## 4. Review Rescue

- [x] 4.1 Fix review cycle 1 blocker R1 by documenting explicit `--no-push`
  manifest update guidance and enforcing `publish.status: skipped` manifests to
  include `payload_commit`, `published_commit`, `reason` and `mode: local-only`.
- [x] 4.2 Extend manifest derive smoke with positive and negative skipped
  local-only publish ledger fixtures.
- [x] 4.3 Fix review cycle 2 blocker R1 by enforcing `publish.status: pushed`
  manifest ledgers to include `payload_commit`, `published_commit`, `remote`,
  `branch` and `pushed_at`; add status-only and missing-`pushed_at` negative
  fixtures for validate and `publish-update`.
