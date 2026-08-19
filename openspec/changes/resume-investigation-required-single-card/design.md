## Context

The existing single-card `resume` command validates only a prior remote
publish-target preflight failure. A fresh `run` requires an ordinary clean
workspace, so it cannot continue a deliberate retained dirty payload after
`investigation_required`.

This change depends on `record-investigation-required-payload-identity`: resume
needs a prior status whose `retained_payload` object can be validated against
the current workspace.

## Goals / Non-Goals

**Goals:**

- Add a second explicit single-card resume branch for prior
  `investigation_required` status records.
- Allow the exact retained dirty working tree only when its fingerprint still
  matches the prior status.
- Prove published investigation and authorization sources are tracked and clean
  at `HEAD` before review/publish continuation.
- Continue at the review/publish boundary without re-running implementation or
  treating a checkpoint commit as evidence.

**Non-Goals:**

- No general dirty-tree launch for ordinary `run`, `preflight`, remote resume
  or queue starts.
- No authorization override from CLI flags, branch names, stash names or prose.
- No automatic creation of investigation or authorization cards.

## Decisions

1. Keep the existing `resume` command surface and classify the prior blocked
   status by reason. Remote publish-target failures keep the existing path.
   `investigation_required` enters a separate retained-payload path. Alternative
   considered: add a new top-level command. Reusing `resume` keeps the operator
   model simple while prior status validation disambiguates behavior.

2. Split clean-tree preflight into two checks for this branch. Automation
   authority, launcher, configuration, symlink, permission and publish-target
   checks still run fresh. The ordinary clean-tree check is replaced by exact
   retained-payload fingerprint validation. This is a narrow exception for the
   previously recorded dirty review target.

3. Validate authorization artifacts at `HEAD`. The runner should verify that the
   referenced investigation and authorization cards are under `4.done`, tracked
   in `HEAD`, unchanged in index/worktree, and relation-matched to the current
   successor card. This keeps the dirty implementation payload separate from
   the clean tracked authorization source.

4. Resume review/publish, not implementation. After retained-payload and
   authorization checks pass, the runner should launch the lifecycle continuation
   that starts at deterministic review preflight and proceeds through review and
   publish. It must not rerun `do` or accept an unreviewed checkpoint commit as
   a reviewed tree.

5. Emit stable machine reasons for every fail-closed branch. Expected reasons
   include prior-status invalidity, card/workspace mismatch, missing retained
   identity, fingerprint drift, missing/stale authorization, relation mismatch
   and authorization ceiling violation.

## Risks / Trade-offs

- [Risk] Allowing any dirty tree in an automation runner is dangerous.
  Mitigation: allow only the exact fingerprinted dirty tree from the prior
  status and fail closed on any drift.
- [Risk] Authorization cards can be published in `HEAD` while unrelated dirty
  files remain. Mitigation: check the authorization and investigation paths are
  individually clean against `HEAD`.
- [Risk] A resume branch might accidentally re-run implementation.
  Mitigation: encode the continuation boundary in specs and smoke tests.

## Migration Plan

- Add retained-payload resume validation to `bin/changerail-delivery-runner`.
- Extend status/preflight checks with stable resume diagnostics.
- Add focused synthetic smokes for successful retained resume and adversarial
  wrong card, wrong workspace, stale authorization and fingerprint drift cases.

## Open Questions

- none
