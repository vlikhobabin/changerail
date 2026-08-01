## Context

`bin/changerail-delivery-runner` already performs a remote-push publish target
check in `publish_target_state`, writes preflight checks into
`changerail.delivery-run.v1` status, and lets queue `preflight-plan` call the
single-card `preflight` command for each card. The current remote failure path
stores a compact generic `detail` from `git ls-remote`, so operators cannot
tell whether the stop was SSH config, DNS, auth, missing branch, timeout or
unknown failure without reading raw logs. Queue status only mirrors the failed
child check reason.

This change stays in generic ChangeRail core. It must not store credentials,
raw remote URLs with userinfo, raw stderr, local runtime reports or
machine-specific paths in tracked files.

## Goals / Non-Goals

**Goals:**
- Classify remote publish-target preflight failures into stable classes.
- Store bounded sanitized evidence in delivery-run status using existing
  canonical fields.
- Retry only transient remote classes with a small bounded backoff.
- Add an explicit single-card `resume` command that consumes prior status,
  repeats full fresh preflight, and continues only after the target is proven.
- Surface remote preflight diagnostics through queue preflight/status without
  embedding child logs.
- Cover all failure classes and later-success resume with local/offline smokes.

**Non-Goals:**
- Infinite retry or autonomous credential repair.
- Credential storage, SSH policy bypass or silent replacement of operator SSH
  config.
- New top-level delivery-run aliases such as `id`, `status` or `started_at`.
- Network-dependent smoke coverage.

## Decisions

1. **Remote preflight evidence lives inside the existing preflight check.**
   The `publish target` check message remains compact for existing readers, but
   the schema gains optional structured fields on check entries:
   `result`, `remote`, `branch`, `remote_url_class`, `failure_class`,
   `detail`, `attempts`, `retryable` and `evidence`. This preserves canonical
   `changerail.delivery-run.v1` shape without duplicate top-level aliases.

2. **Classification is derived from sanitized `git ls-remote` results.**
   The runner classifies timeout directly from `TimeoutExpired`; missing branch
   from `ls-remote --exit-code` exit `2` with no stderr; DNS from known resolver
   diagnostics; auth from permission/authentication denied messages; SSH config
   from SSH config/identity/known-host/key exchange setup diagnostics; and
   unknown remote failure as the fail-closed fallback. Stored detail is bounded
   through existing compaction/redaction helpers and never includes raw remote
   URLs.

3. **Retry/backoff is narrowly allowlisted.**
   Only DNS, timeout and unknown remote failure receive bounded retry attempts.
   Auth, SSH config and missing branch stop immediately because retrying does
   not prove authority and may hide operator configuration problems.

4. **Single-card resume is explicit and proof-driven.**
   A new `resume` subcommand accepts `--status-path` for a prior blocked
   `changerail.delivery-run.v1` record, derives the card/workspace/run mode from
   that record and current arguments, runs the same full preflight as `run`, and
   launches delivery only if preflight now passes. Prior status is evidence for
   operator context, not authority to skip checks.

5. **Queue resume keeps using child records.**
   `resume-plan` already re-resolves cards and invokes children. It should not
   trust a stale child preflight result; queue diagnostics should reference the
   current child status path and compact failure class after fresh child
   preflight/run attempts.

## Risks / Trade-offs

- **Risk:** Git and SSH diagnostics vary by platform and locale.
  **Mitigation:** Use stable exit conditions first, broad keyword matching only
  for classification, and retain `unknown_remote_failure` as fail-closed.

- **Risk:** Structured evidence could accidentally expose credentials.
  **Mitigation:** Store URL class, remote name, branch, bounded class/detail and
  argv summary only; never store raw remote URL, stdout or stderr in status.

- **Risk:** Retry can mask auth or branch uncertainty.
  **Mitigation:** Retry only transient classes and keep auth/branch/SSH config
  classes non-retryable.

- **Risk:** `resume` may be mistaken for a force continuation.
  **Mitigation:** The command fails before launch unless a fresh preflight
  proves the publish target under current workspace state.

## Migration Plan

1. Extend schemas to accept optional structured preflight evidence on existing
   check entries.
2. Refactor runner remote preflight into classifiable attempt/evidence helpers.
3. Add bounded retry/backoff and explicit `resume`.
4. Extend queue diagnostics to preserve compact failure class and child status
   reference.
5. Add local smokes for each failure class and later-success resume.
6. Update docs and sync specs before archive.

## Open Questions

- none
