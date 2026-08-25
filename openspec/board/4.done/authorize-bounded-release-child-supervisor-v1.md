# Авторизовать bounded release child supervisor v1

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 02R10-S

## Source
- Exact published rescue `rescue-release-process-supervisor-boundary`, commit
  `ea7eb235b95356ecd86afc98a0db8b48ea6243e9`.

## Summary
Опубликовать один bounded authorization source для будущего platform-neutral
child protocol и POSIX child supervision, не создавая successor и не включая
его в release-facing wiring до exact published A3.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Planning: fresh `gpt-5.6-sol`/`high`
- Implementation: docs-only deterministic
- Independent review: fresh `gpt-5.6-sol`/`high`
- Same-card repair/rescue budget limit/used/remaining: `1/0/1`, exhausted `false`

## Depends On
- `rescue-release-process-supervisor-boundary`

## Blocks
- `implement-bounded-release-child-supervisor-v1`

## Authorization
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/rescue-release-process-supervisor-boundary.md","investigation_id":"rescue-release-process-supervisor-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-release-child-supervisor-v1.md","successor_id":"implement-bounded-release-child-supervisor-v1","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- One exact six-field source binds the published rescue to only
  `implement-bounded-release-child-supervisor-v1`; the rescue blocks both this
  authorization and its future successor, and this authorization depends on
  the rescue and blocks only that successor.
- A later successor uses only
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-release-child-supervisor-v1.md","authorization_id":"authorize-bounded-release-child-supervisor-v1"}`
  in `Published investigation authorization`, and remains at `<=499` added
  production LOC relative to the exact remote-reachable HEAD that publishes
  this authorization.
- Future S owns only the platform-neutral child protocol and POSIX hard
  stdout/stderr/report framing, process-group containment, finite deadline,
  TERM-then-KILL escalation, reap and subreaper cleanup.
- S excludes Git parsing, scheduler policy, Windows Job behavior, registry,
  baseline/CI activation, receipt ownership and any live, credential or
  mutation authority; scope overlap fails closed.
- Until exact A3 is published and remote-reachable, S remains structurally
  dormant: `run-release-baseline`, workflow, review/publish gates and receipt
  schema neither import nor invoke it.
- This authorization and its OpenSpec artifacts add production, test and
  runtime LOC `0`; successor card/code remain absent.

## Change Set
- `authorize-bounded-release-child-supervisor-v1`

## Verify
- GREEN: strict target/capability/all OpenSpec validation; exact-object,
  relation, absence and ownership oracle; `.mcp.json` JSON and
  `.codex/config.toml` TOML parsing.
- GREEN: current-only public-surface scan, source classification, tracked and
  explicit-untracked whitespace, manifest validation/scope and normalized
  ordinary/high preflight after archival handoff.
- Do not run history scan, full release baseline, live execution, review,
  commit or push.

## Archive
- `openspec/changes/archive/2026-08-25-authorize-bounded-release-child-supervisor-v1/`

## Related
- `openspec/board/4.done/rescue-release-process-supervisor-boundary.md`
- `openspec/changes/archive/2026-08-25-authorize-bounded-release-child-supervisor-v1/`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
Delivery завершен: exact six-field authorization source, reciprocal lineage,
future two-field reference, closed S ownership and A3 dormancy сохранены;
`changerail-release-ci` synchronized and sole docs-only change archived.
Successor card/code remain absent. Production, test and runtime additions remain
`0` LOC. Payload готов к fresh independent ordinary review.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `authorize-bounded-release-child-supervisor-v1`

### Why
S is the first implementation foundation in the published rescue lineage and
needs one separately published, bounded authorization source before its future
successor can exist.

### Goal
Publish the exact authorization and dormant ownership contract for future S
without creating or implementing that successor.

### Scope
- Board/OpenSpec/spec relationship docs only; production, test and runtime LOC
  `0`.

### Acceptance
- The exact six-field source, reciprocal lineage, exact future two-field
  reference and `<=499` published-authorization-HEAD limit are retained.
- S is limited to the platform-neutral child protocol and POSIX hard
  stdout/stderr/report/process/deadline/TERM-KILL/reap/subreaper boundary;
  Git, scheduler, Windows Job, registry, baseline/CI and receipt ownership are
  excluded.
- Successor/card/code remain absent and S remains structurally dormant until
  exact published A3.

### Depends On
- `rescue-release-process-supervisor-boundary`

### Related
- `openspec/changes/archive/2026-08-25-authorize-bounded-release-child-supervisor-v1/`

## Log
- 2026-08-25 FF created one same-slug docs-only authorization card from the
  exact published rescue base; successor remains absent.
- 2026-08-25 DO synchronized the exact `changerail-release-ci` requirement,
  archived only this same-slug docs-only change and completed strict/current
  verification. No history/full/live execution, successor, review, commit or
  push occurred.
- 2026-08-25T20:49:13Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
