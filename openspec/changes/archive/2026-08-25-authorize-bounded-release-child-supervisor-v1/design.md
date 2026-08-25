## Context

Published rescue `rescue-release-process-supervisor-boundary` fixes the clean
future order S -> (H4, I3, W1) -> R3 -> A3 and explicitly reserves the first
foundation for child supervision. The rescue is an investigation decision, not
the parser-recognized authorization source required by deterministic preflight
for a future bounded implementation. This change supplies that source without
creating a future implementation card or changing an executable surface.

## Goals / Non-Goals

**Goals:**

- Publish exactly one six-field `Investigation authorization` object bound to
  the rescue and the one future S successor.
- Preserve reciprocal rescue/authorization/successor relationships and the
  future successor's exact two-field reference.
- Reserve S exclusively for the platform-neutral child protocol and POSIX
  hard stdout/stderr/report framing, process containment, deadline,
  TERM-then-KILL escalation, reaping and subreaper cleanup.
- Keep S structurally dormant until exact A3 is published and remote-reachable.
- Keep this authorization docs-only with production, test and runtime LOC `0`.

**Non-Goals:**

- Do not create or implement
  `implement-bounded-release-child-supervisor-v1`.
- Do not add a new parser, schema, authority, wire protocol, executable
  command, workflow, registry, receipt or activation point.
- Do not own Git parsing, scheduler policy, Windows Job behavior, release
  registry, canonical baseline/CI activation or receipt handling.
- Do not run or cite reachable-history, full-release, live execution, review,
  commit or push activity as authorization evidence.

## Decisions

### 1. The authorization card is the only future-S authority source

The `3.inprogress` authorization card contains one parser-owned inline object
with exactly these fields and values:

```json
{"investigation_card":"openspec/board/4.done/rescue-release-process-supervisor-boundary.md","investigation_id":"rescue-release-process-supervisor-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-release-child-supervisor-v1.md","successor_id":"implement-bounded-release-child-supervisor-v1","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

No alternate object, extra field, source card or implementation payload is an
authority source. The authorization card depends on the rescue and blocks only
the exact future successor; the published rescue already blocks both cards.

### 2. Future S has one narrow protocol-and-POSIX boundary

The future implementation may define the platform-neutral child protocol and
POSIX hard stdout/stderr/report framing, process group containment, finite
deadline, TERM-then-KILL escalation, reaping and subreaper cleanup. It must
fail closed when an input or requested responsibility falls outside that
boundary. Git parsing/framing, scheduler policy and ordering, Windows Job
control, registry/profile selection, baseline/CI activation and receipt
ownership remain assigned to later distinct owners.

### 3. The future reference and LOC base are publication-bound

Only after this authorization is published and remote-reachable may a separate
flow create the future successor. That future card must depend on the rescue
and contain only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-release-child-supervisor-v1.md","authorization_id":"authorize-bounded-release-child-supervisor-v1"}
```

The `500` ceiling is an authorization-gate threshold, not permission for 500
production lines: future S remains `<=499` added production LOC relative to the
exact remote-reachable HEAD that publishes this source.

### 4. Structural dormancy defers every release-facing activation to A3

Before exact A3 is published and remote-reachable, `run-release-baseline`, the
CI workflow, review/publish gates and receipt schema must neither import nor
invoke S. Only exact A3 integration paths may activate the published foundation
after that point. This leaves the docs-only authorization observable through
focused static/current verification without inventing early release authority.

## Risks / Trade-offs

- **[Risk] A future card mutates the exact relation or adds a third reference
  field.** -> Deterministic preflight rejects every id, path, field-count or
  reciprocal-relation mismatch.
- **[Risk] POSIX supervision absorbs policy or release ownership.** -> The
  contract names allowed operations and excludes Git, scheduler, Windows Job,
  registry, baseline/CI and receipt scope; overlap fails closed.
- **[Risk] Dormant code is wired into a release path early.** -> Negative
  wiring remains mandatory until exact published A3 is the only activation
  owner.
- **[Risk] `500` is treated as an implementation budget.** -> The future
  requirement states the stricter `<=499` production-LOC limit against the
  published authorization HEAD.

## Migration Plan

1. Complete and validate this same-slug docs-only change.
2. Sync the release-CI delta, archive the change and leave the authorization
   card in `3.inprogress` for independent ordinary review.
3. Publish the reviewed card; its remote-reachable HEAD becomes the future
   S comparison base.
4. Only a later separate flow may create the future successor with the exact
   two-field reference; before exact A3 it remains unwired from release paths.

Before publication, rollback removes only this unpublished documentation.
After publication, any altered relation or scope requires a new tracked
authorization instead of mutating the published source.

## Open Questions

None. The published rescue fixes the authorization identity, ownership split,
order and dormancy boundary.
