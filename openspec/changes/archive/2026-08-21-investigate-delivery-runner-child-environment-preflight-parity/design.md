## Context

Existing runner preflight already checks launcher readiness, Codex auth,
effective project policy, symlinks, executable permissions and remote
publish-target reachability. Queue `preflight-plan` also invokes a single-card
preflight and propagates compact child status into aggregate status.

The observed gap is narrower: the supervisor process can prove the configured
remote through its own Git and SSH resolution, while the later Codex delivery
child repeats the same remote probe from a different execution surface. That
surface can differ by launcher environment, `CODEX_HOME`, `CODEX_WORKDIR`,
permission profile, command sandbox, Git environment/config, SSH config,
identity lookup, known-hosts policy and agent/socket availability. A
supervisor-only `git ls-remote` proof is therefore not the same proof as a
child-equivalent publish-target proof.

The public-safe deterministic reproducer for the investigation is:

1. Create a temporary repository with a local bare upstream and confirm the
   supervisor probe passes:
   `git ls-remote --exit-code origin refs/heads/main`.
2. Re-run the same repository, branch and configured remote through a
   child-equivalent profile that changes only child-visible Git/SSH resolution
   by injecting an isolated `GIT_CONFIG_GLOBAL` or fake `git ls-remote` wrapper
   into the child launcher environment.
3. Make the child-equivalent probe return a sanitized SSH configuration failure
   such as `Bad configuration option: Include`.
4. Assert that the aggregate admission result is blocked before workspace lock
   creation or delivery child launch, records failure class `ssh_config`, marks
   it non-retryable and references structured child status instead of raw logs.

This reproducer does not require a real credential, a private remote, a live
provider or machine-local runtime records. It models the exact class of
failure: same workspace/card/branch intent, different child-visible
Git/SSH resolution.

## Goals / Non-Goals

**Goals:**

- Publish a decision-only investigation for supervisor/child preflight parity.
- Inventory boundaries that can affect publish-target proof.
- Select one canonical child-equivalent preflight design.
- Define receipt binding and bounded freshness.
- Define dispatch-time revalidation for long serial queues.
- Preserve structured failure classes, retryability and resumability.
- Bind one exact implementation successor and verification floor.

**Non-Goals:**

- No production runner, launcher, schema, skill or smoke implementation changes
  in this card.
- No real SSH credential, private remote or host-specific diagnostic is used as
  evidence.
- No generic default such as `ssh -F /dev/null` is introduced.
- No package-managed system SSH files are modified.
- No remote failure silently selects `--no-push`.

## Decisions

1. **Use a child-equivalent preflight receipt, not supervisor-only proof.**
   The successor should extend queue admission and resume preflight so each
   unresolved card receives a pre-delivery receipt from the same effective
   child execution profile that the delivery child will use. The receipt is
   still a preflight artifact, not delivery: it must run before workspace locks
   and before the live `$changerail-deliver` child.

   Rejected alternative: trust aggregate supervisor `git ls-remote`. It cannot
   see child-specific Git/SSH/sandbox differences.

   Rejected alternative: launch a full delivery child to discover the failure.
   That preserves the current late stop and can create locks/runtime state
   before predictable environment blockers are known.

2. **Bind the receipt to existing status surfaces where possible.** The
   successor should reuse `changerail.delivery-run.v1` preflight status as the
   child-equivalent receipt and reference it from
   `changerail.delivery-plan-status.v1` via `run_status_path` and
   `failure_class`. The pass/fail check remains named `publish target` and uses
   existing structured fields: `remote`, `branch`, `remote_url_class`,
   `failure_class`, `retryable`, `attempts`, `detail` and `evidence`.

   The receipt must be bound to workspace root, card id/path, current `HEAD`,
   branch, upstream remote, remote URL class, launcher path, selected
   `CODEX_WORKDIR`, effective `CODEX_HOME` policy, permission profile and a
   sanitized Git/SSH profile fingerprint. This can be encoded within the
   existing command/status/evidence fields; if the successor needs new required
   schema fields, it must declare a new runner/status protocol boundary and use
   the repository's published-investigation authorization route.

3. **Use a bounded freshness window plus dispatch-time revalidation.** A
   child-equivalent pass is valid only for immediate queue admission and for a
   bounded interval. The successor should default the interval to 300 seconds
   and allow a documented environment override only for tests. Before each
   later serial dispatch, `run-plan` and `resume-plan` must rerun the
   child-equivalent publish-target proof for that card. Stale receipts are
   evidence, not authority.

4. **Keep terminal status specific and resumable.** A child-equivalent preflight
   failure should terminate the aggregate run as `BLOCKED` with
   `terminal_reason: publish_target_preflight_failed`; the affected card status
   must retain the sanitized `failure_class`, `retryable`, attempt count and
   child `run_status_path`. The runner must not fall back to
   `unpublished_card` when the real blocker is a preflight failure.

5. **Retry only transient remote classes.** DNS, timeout and unknown transient
   transport failures may use the existing bounded retry/backoff policy.
   Authentication, SSH configuration/policy and missing branch remain
   non-retryable fail-closed classes. Retry attempt counts are part of the
   receipt.

6. **Support SSH overrides only as explicit consumer-scoped inputs.** A
   successor may support a consumer-owned SSH/Git override only when it is
   explicit, workspace-scoped, sanitized in status and never installed as a
   generic ChangeRail default. The override must not bypass host policy, read
   credentials into tracked artifacts or modify package-managed system SSH
   files. Diagnostics may name classes like `ssh_config`; they must not expose
   identity paths, userinfo, tokens or raw config contents.

7. **Bind one implementation successor.** The exact successor id is
   `add-delivery-runner-child-equivalent-preflight`. The current queue path is
   `openspec/board/1.backlog/add-delivery-runner-child-equivalent-preflight.md`;
   after triage its deliver-ready path should be
   `openspec/board/2.todo/add-delivery-runner-child-equivalent-preflight.md`.
   The successor production LOC ceiling is 300 added production-counted lines
   and its protocol-boundary declaration is `no`: it must reuse existing status
   schema fields. If implementation needs more than 300 production-counted LOC
   or any new required runner/status wire fields, it must stop for a separate
   published authorization bound to this investigation and the exact successor.

## Risks / Trade-offs

- [Risk] A child-equivalent probe can become as expensive as a delivery launch.
  Mitigation: keep it mutation-free, bounded and status-producing, and run it
  before locks or delivery children.
- [Risk] Encoding profile binding in existing fields may be less ergonomic than
  new schema fields. Mitigation: the successor can stay under the no-protocol
  boundary first; if structured schema changes are required, the existing
  investigation-authorization route is explicit.
- [Risk] Retryable failures could hide persistent environment problems.
  Mitigation: retries remain bounded and class-specific; SSH/auth/branch
  classes are never auto-retried.
- [Risk] SSH override support could become a generic bypass. Mitigation: require
  explicit consumer scope, sanitized evidence and no modification of host or
  package-managed SSH policy.

## Migration Plan

- Publish this investigation decision and archive the OpenSpec change.
- Keep the successor in backlog until a maintainer confirms the no-protocol,
  <=300 production-LOC boundary is still realistic.
- Move the successor to `2.todo` only with the verification floor from this
  decision.
- If implementation crosses the declared boundary, create a separate
  authorization card before continuing the successor.

## Open Questions

- none
