# Исследование parity preflight среды дочернего delivery runner

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- none

## Series Index
- none

## Source
- Sanitized field observation from a supervised consumer package run: the
  aggregate publish-target preflight passed, while the first child delivery
  worker failed the equivalent Git remote probe inside its Codex execution
  surface before planning or implementation began.
- The child changed no tracked files, the workspace lock was released, and the
  aggregate queue stopped fail-closed with all dependent cards still pending.

## Summary
Investigate why the delivery-plan supervisor and the child Codex execution
surface can produce different publish-target results for the same repository,
branch and remote. Define a child-equivalent, freshness-bound preflight that
detects environment, sandbox and SSH-policy incompatibility before a package
run is admitted.

The investigation must preserve safety stops. Its goal is to move predictable
environment failures ahead of queue launch, retain precise structured reasons
and keep the same aggregate run resumable after an external condition is
repaired.

## Review
- Risk tier: `ordinary`
- Review effort: `high`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

This card is decision-only. A successor that changes runner/status wire
semantics must declare that boundary separately and use the repository's
investigation-authorization route when required by complexity preflight.

## Blocks
- `add-delivery-runner-child-equivalent-preflight`

## Acceptance
- Reproduce the supervisor/child parity gap with public-safe deterministic
  evidence that does not require a real credential, private remote or
  machine-local runtime record.
- Inventory the execution boundaries that can affect the result: runner
  process, launcher environment, Codex configuration, permission profile,
  sandboxed command execution, Git configuration and SSH configuration
  resolution.
- Select one canonical child-equivalent preflight design and define how its
  receipt is bound to workspace, branch, remote class, execution profile and a
  bounded freshness interval.
- Define dispatch-time revalidation so environment drift during a long serial
  queue is caught before the next child begins.
- Define a structured terminal contract that preserves an exact reason such as
  `publish_target_preflight_failed`, a sanitized failure class such as
  `ssh_config`, and retryability instead of falling back to
  `unpublished_card`.
- Separate retryable DNS, timeout and transient transport failures from
  non-retryable authentication, SSH policy and configuration failures; do not
  introduce an unbounded retry loop.
- Decide whether a consumer-scoped SSH override can be supported explicitly
  without becoming a generic default, bypassing host policy or modifying
  package-managed system SSH files.
- Bind one exact implementation successor id/path, its production LOC ceiling,
  protocol-boundary declaration and the verification floor listed below.

## Required Successor Verification Floor
- Supervisor pass plus child-equivalent fail blocks before aggregate queue
  launch and before a workspace lock or delivery child is created.
- Supervisor and child-equivalent pass admit the queue without weakening the
  existing clean-tree, authority, auth, upstream or remote checks.
- Dispatch-time revalidation catches environment drift before a later card.
- SSH configuration and permission diagnostics are sanitized, classified as
  non-retryable and never expose credentials, identity paths or remote
  userinfo.
- Retryable DNS/timeout failures remain bounded and record attempt counts.
- Child terminal markers survive into single-card and aggregate structured
  status without the `unpublished_card` fallback.
- `resume-plan` continues the same aggregate run after fresh preflight while
  delivered cards remain skipped and pending dependencies remain ordered.
- Explicit `--no-push` retains its existing local-only semantics; remote
  failure must not silently select it.
- POSIX child-environment parity coverage does not regress supported Windows
  runner behavior or custom launcher behavior.

## Non-Goals
- Implementing runner, launcher, schema, skill or test changes in this card.
- Suppressing legitimate review, authority, dirty-tree, publish or external
  safety stops.
- Mutating package-managed system SSH files or prescribing one host-specific
  permission workaround as generic ChangeRail behavior.
- Making `ssh -F /dev/null`, a particular remote provider or a credential
  mechanism the cross-project default.
- Reading, copying or committing authentication material, local runtime logs or
  consumer-specific paths.

## Investigation Decision
The parity gap is real even when repository, branch and configured remote are
nominally the same, because the supervisor and child surfaces resolve Git and
SSH through different process/environment layers. The public-safe deterministic
reproducer is:

- create a temporary Git repository with a local bare upstream and prove that
  the supervisor command
  `git ls-remote --exit-code origin refs/heads/main` passes;
- run the same workspace, branch and configured remote through a
  child-equivalent profile that changes only child-visible Git/SSH resolution
  with isolated `GIT_CONFIG_GLOBAL` or a fake `git ls-remote` wrapper;
- make that child-equivalent proof fail with sanitized SSH configuration
  output such as `Bad configuration option: Include`;
- assert that aggregate admission blocks before workspace lock creation or
  delivery child launch, records `failure_class: ssh_config`, marks it
  non-retryable and references child structured status instead of raw logs.

The execution boundaries that can change the result are runner process,
launcher environment, `CODEX_HOME`, `CODEX_WORKDIR`, Codex project config,
permission profile, sandboxed command execution, Git environment/config
resolution, SSH config/include resolution, identity lookup, known-hosts policy
and SSH agent/socket availability. Supervisor-only `git ls-remote` proof is
therefore insufficient for aggregate queue admission.

The selected design is a pre-delivery child-equivalent receipt. Queue
admission, `run-plan` and `resume-plan` should prove publish-target readiness
through the same effective child execution profile that a delivery child will
use, but still before any workspace lock or live `$changerail-deliver` child is
created. The receipt should reuse existing `changerail.delivery-run.v1`
preflight status and aggregate `changerail.delivery-plan-status.v1`
`run_status_path`/`failure_class` fields when possible. It must bind workspace
root, card id/path, `HEAD`, branch, upstream remote, remote URL class,
launcher, selected `CODEX_WORKDIR`, effective `CODEX_HOME` policy, permission
profile and sanitized Git/SSH profile. A passing receipt is fresh only for the
immediate admission window; the successor should default that bounded window
to 300 seconds and rerun the proof before each later serial dispatch.

If child-equivalent publish-target proof fails, aggregate status should stop as
`BLOCKED` with `terminal_reason: publish_target_preflight_failed`. The affected
card status must preserve the sanitized remote `failure_class`, retryability,
attempt count and child status reference; it must not degrade to
`unpublished_card`. Retry remains bounded to DNS, timeout and transient
transport classes. Authentication, SSH policy/configuration and missing branch
remain non-retryable fail-closed classes.

Consumer-scoped SSH/Git overrides can be supported only as explicit
workspace-scoped inputs. They must not become ChangeRail defaults, bypass host
policy, modify package-managed system SSH files, read credential contents into
tracked artifacts or expose identity paths, URL userinfo, tokens or raw config
contents in status.

The exact implementation successor is
`add-delivery-runner-child-equivalent-preflight`; its current path is
`openspec/board/1.backlog/add-delivery-runner-child-equivalent-preflight.md`.
The successor production LOC ceiling is 300 added production-counted lines and
its runner/status protocol-boundary declaration is `no`: it should reuse
existing status schema fields. If the implementation needs more than 300
production-counted LOC or any new required runner/status wire fields, it must
stop for a separate published authorization bound to this investigation and
the exact successor.

## Change Set
- `openspec/changes/archive/2026-08-21-investigate-delivery-runner-child-environment-preflight-parity/`

## Verify
- GREEN: retained deterministic parity reproducer via `bin/changerail-evidence
  capture --id deterministic-parity-reproducer ...` -> supervisor pass,
  child-equivalent fail, `failure_class=ssh_config`, retryable false.
- GREEN: `bin/changerail-evidence validate
  .runtime/changerail/evidence/investigate-delivery-runner-child-environment-preflight-parity/index.json
  --json` -> 1 entry.
- GREEN: `./bin/openspec validate
  "investigate-delivery-runner-child-environment-preflight-parity" --strict`.
- GREEN: `./bin/openspec validate "changerail-delivery-runner" --strict`.
- GREEN: `./bin/openspec validate --all --strict` -> 24/24 passed before
  archive.
- GREEN: `./bin/openspec validate --all --strict` -> 23/23 passed after
  archive.
- GREEN: `bin/changerail-delivery-manifest scope-check
  .runtime/changerail/delivery-manifests/investigate-delivery-runner-child-environment-preflight-parity.json
  --workspace . --target working-tree --json`.
- GREEN: `python3 scripts/public-surface-scan.py` -> 1101 files scanned, 0
  findings.
- GREEN: `python3 -m json.tool .mcp.json`.
- GREEN: TOML parse for `.codex/config.toml`.
- GREEN: `git diff --check`.
- GREEN: explicit trailing-whitespace scan over untracked files -> 7 files.
- Fresh independent ordinary/high review before scoped publish.

## Archive
- `openspec/changes/archive/2026-08-21-investigate-delivery-runner-child-environment-preflight-parity/`

## Related
- `bin/changerail-delivery-runner`
- `bin/codex`
- `schemas/changerail-delivery-run.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `scripts/smoke-delivery-runner.py`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `docs/consumer-adoption-runbook.md`
- `openspec/changes/archive/2026-08-21-investigate-delivery-runner-child-environment-preflight-parity/`
- `openspec/board/1.backlog/add-delivery-runner-child-equivalent-preflight.md`

## Result
published; investigation decision complete

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `investigate-delivery-runner-child-environment-preflight-parity`

### Why
The aggregate runner currently proves publish-target readiness in the
supervisor process, but the delivery worker repeats that gate inside a Codex
execution surface whose environment and SSH configuration resolution may
differ. A green package preflight can therefore be followed immediately by a
predictable child safety stop.

### Goal
Publish a public-safe architecture decision for child-equivalent preflight,
freshness, dispatch-time revalidation, failure taxonomy and resumability, then
bind one bounded implementation successor.

### Scope
- Produce a deterministic environment-parity reproducer.
- Map supervisor, launcher and sandbox execution boundaries.
- Compare viable preflight placement and receipt-binding designs.
- Specify structured failure classification and bounded retry behavior.
- Select and bind the exact implementation successor and verification floor.
- Do not modify production runner behavior in this investigation.

### Acceptance
- The decision explains the observed parity gap without relying on private
  consumer evidence.
- The selected design detects the gap before aggregate work begins and catches
  later environment drift before dispatch.
- Structured status retains the real sanitized blocker and retryability.
- The successor contract preserves fail-closed publish and resume behavior.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-08-21-investigate-delivery-runner-child-environment-preflight-parity/`

## Log
- 2026-08-21T07:06:02Z created from a sanitized supervised package-runner
  preflight-parity finding; implementation and tests intentionally deferred to
  a separate ChangeRail successor.
- 2026-08-21T09:29:17Z `$chrl-ff` created apply-ready OpenSpec artifacts for
  `investigate-delivery-runner-child-environment-preflight-parity` and prepared
  delivery handoff.
- 2026-08-21T09:35:22Z `$chrl-do` recorded the investigation decision, created
  successor `add-delivery-runner-child-equivalent-preflight`, synced
  `changerail-delivery-runner`, archived the OpenSpec change and prepared
  review handoff.
- 2026-08-21T09:41:44Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
