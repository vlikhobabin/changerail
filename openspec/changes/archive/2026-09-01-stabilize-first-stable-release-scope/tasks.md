## 1. Normalize Deferred Board Scope

- [x] 1.1 Move `implement-phase-routed-delivery-authorization-boundary` from
  `2.todo` to `5.canceled`, record `superseded/deferred`, and remove any live
  delivery handoff without rewriting published investigation history.
- [x] 1.2 Create one backlog-only phase-routed reconsideration card whose entry
  gates require a published stable release, reduced project debt, confirmed
  consumer demand and fresh bounded triage; do not create authorization or
  implementation artifacts.
- [x] 1.3 Add an explicit debt entry gate to
  `manage-runtime-artifact-retention-and-cleanup` and make its next action wait
  for a separate operator decision after debt reduction.
- [x] 1.4 Move the obsolete live
  `implement-bounded-public-history-scan-runtime` todo to `5.canceled` as
  superseded by the published replacement card; create no stale investigation
  or implementation handoff.

## 2. Align Stable Release Documentation And Handoff

- [x] 2.1 Update `README.md` status and roadmap so the first stable candidate
  is the clean reviewed generic core and deferred phase-routed/retention work
  is not described as ready or release-blocking.
- [x] 2.2 Update `docs/release-discipline.md` with the clean-core candidate
  rule, ignored local-inventory boundary and separate final-certification
  release-card requirement.
- [x] 2.3 Create a separate deliver-ready `prepare-1-0-0-stable-release` board
  card for version/changelog/compatibility/migration, distribution metadata,
  trusted checks, final review, tag and publication after this card is done.

## 3. Inventory And Verify The Clean Candidate

- [x] 3.1 Generate a machine-local branch/worktree inventory only under
  ignored `.runtime/changerail/release-scope/`, classify clean/dirty and
  merged/ahead state without copying paths or private names into tracked
  files, and perform no destructive cleanup in this change.
- [x] 3.2 Install pinned development dependencies into the ignored release
  venv, reproduce the exact working payload in an isolated clone limited to
  release refs, and run core then extended release suites sequentially on 2
  CPUs; retain raw output under ignored evidence and stop for a separate fix
  card if a candidate-owned runtime blocker appears.
- [x] 3.3 Run `python3 scripts/public-surface-scan.py`,
  `python3 scripts/public-surface-scan.py --history`, JSON/TOML parsing and
  `git diff --check`, including explicit whitespace checks for untracked
  artifacts.

## 4. Sync, Archive And Prepare Review

- [x] 4.1 Sync only this change's `changerail-release-discipline` delta into
  the main spec, validate the capability and all OpenSpec artifacts strictly,
  then archive `stabilize-first-stable-release-scope` through the normal
  lifecycle.
- [x] 4.2 Update the board card with exact archive path, concise verification
  outcomes and manifest/evidence handoff; leave it in `3.inprogress` for fresh
  independent review.
- [x] 4.3 Derive and scope-check the delivery manifest, run deterministic
  review preflight on the frozen payload and require a fresh independent
  `GO` before publish/finalization.
