# Определить границу bounded micro-fix для неопубликованного terminal payload

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 02R10-S2R

## Source
- Published psutil S2 decision `rescue-psutil-release-child-supervisor-boundary`.
- Published psutil S2 authorization
  `authorize-psutil-backed-release-child-supervisor-v2`.
- The unpublished `implement-psutil-backed-release-child-supervisor-v2`
  candidate is forensic input only. Its first review cycle closed R1-R6 through
  one repair; its second cycle introduced one new isolated R7 blocker: pipe
  EOF was treated as completion while the leader remained live. The payload
  was never committed or pushed and has no receipt or public authority.

## Summary
Зафиксировать узкое reusable decision boundary: только один новый authorization
source может разрешить один clean v3 micro-fix, который механически использует
замороженный failed candidate только как source material и заново доказывает
весь R1-R7 контракт.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Implementation: docs-only deterministic
- Independent review: one fresh `gpt-5.6-sol`/`high` pending
- Same-card repair/retry/rescue budget limit/used/remaining: `0/0/0`, exhausted `true`

## Depends On
- `rescue-psutil-release-child-supervisor-boundary`
- `authorize-psutil-backed-release-child-supervisor-v2`

## Blocks
- `authorize-bounded-psutil-supervisor-micro-fix-v3`
- `deliver-psutil-backed-release-child-supervisor-v3`
- downstream refresh remains blocked until S3 is published.

## Authorization
- Future authorization object, to be created only in the later exact
  authorization card:
  `{"investigation_card":"openspec/board/4.done/decide-bounded-unpublished-terminal-micro-fix-boundary.md","investigation_id":"decide-bounded-unpublished-terminal-micro-fix-boundary","successor_card":"openspec/board/3.inprogress/deliver-psutil-backed-release-child-supervisor-v3.md","successor_id":"deliver-psutil-backed-release-child-supervisor-v3","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`
- The future authorization MUST depend on this decision and block only
  `deliver-psutil-backed-release-child-supervisor-v3`. That successor MUST
  depend on this decision and the future authorization, and use only
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-psutil-supervisor-micro-fix-v3.md","authorization_id":"authorize-bounded-psutil-supervisor-micro-fix-v3"}`.

## Acceptance
- This decision blocks the exact future authorization and v3 successor, and
  preserves their reciprocal dependency and exact six-field/two-field objects.
- One micro-fix successor is allowed only when the candidate is unpublished,
  the exact published authorization is valid, all prior findings are
  independently closed, and the latest cycle has exactly one new isolated
  blocker. It stays within its exact authorized production paths and at most
  499 added production LOC against its own authorization-publishing HEAD.
- The successor has no credential, mutation, live or final authority; no
  scope, dependency, schema or ownership expansion; and no terminal evidence
  reuse. It starts clean from the new authorization HEAD, may mechanically
  reconstruct executable code and tests from the frozen failed candidate only
  as source material, and reruns every connected R1-R7 proof without reusing
  verdict, history, log, receipt or manifest.
- R7 treats pipe EOF as stream state only. Completion requires observing the
  leader terminal state or reaching execution timeout, then cleanup.
- The v3 successor gets one implementation attempt and one fresh Sol/high
  review, with repair/retry/rescue budget `0/0/0`. S3 remains dormant and all
  downstream refresh work stays blocked pending its publication.
- This decision creates no authorization or successor card, adds production,
  test and runtime LOC `0`, and retains only generic forensic facts.

## Change Set
- `decide-bounded-unpublished-terminal-micro-fix-boundary`

## Verify
- GREEN: strict change, `changerail-release-ci` and all OpenSpec validation.
- GREEN: exact object field-count/order, future-card absence, source-material
  boundary, R1-R7 fresh-proof rule, R7 EOF semantics and dormant refresh
  blocking are statically represented in the release-CI contract.
- GREEN: `.mcp.json` JSON and `.codex/config.toml` TOML parsing, current-only
  public-surface and source-classification scans, tracked plus explicit
  untracked whitespace, ignored-manifest validation/scope and normalized
  ordinary/high preflight.
- This docs-only delivery does not run or accept history, full release
  baseline, live execution, authorization card, successor, review, commit or
  push evidence.

## Archive
- `openspec/changes/archive/2026-08-26-decide-bounded-unpublished-terminal-micro-fix-boundary/`

## Related
- `openspec/board/4.done/rescue-psutil-release-child-supervisor-boundary.md`
- `openspec/board/4.done/authorize-psutil-backed-release-child-supervisor-v2.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
DO completed: one docs-only decision change synchronized four bounded
`changerail-release-ci` requirements and was archived. The exact future v3
lineage, clean reconstruction boundary, fresh R1-R7 proof rule, R7
leader-terminal-or-timeout completion rule and dormant downstream refresh gate
are retained. Production/test/runtime LOC: `0`. Future authorization and
successor cards/code remain absent. The payload is pending one fresh independent
ordinary/high review.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `decide-bounded-unpublished-terminal-micro-fix-boundary`

### Why
The unpublished authorized S2 candidate exhausted its allowed cycle and its
sole new R7 blocker needs a clean, narrow successor boundary rather than a
resume or publication of terminal material.

### Goal
Publish one docs-only decision that permits exactly one future v3 micro-fix
authorization and successor under a fresh, independently re-proved contract.

### Scope
- This card, same-slug OpenSpec artifacts, synchronized `changerail-release-ci`
  specification and archive metadata only; production/test/runtime LOC `0`.

### Acceptance
- Exact future authorization/successor lineage, clean-start source-material
  rule, R1-R7 re-proof and R7 terminal-state semantics are retained.
- No authorization or successor artifact, terminal evidence reuse, authority
  expansion, history/full/live proof, review, commit or push is created.

### Depends On
- `rescue-psutil-release-child-supervisor-boundary`
- `authorize-psutil-backed-release-child-supervisor-v2`

### Related
- `openspec/changes/archive/2026-08-26-decide-bounded-unpublished-terminal-micro-fix-boundary/`

## Log
- 2026-08-26 card created from published psutil lineage. The terminal
  unpublished candidate is described only through generic forensic facts.
- 2026-08-26 FF created one same-slug docs-only decision change with proposal,
  design, full release-CI delta and tasks. No future authorization or
  successor artifact, history/full/live evidence, review, commit or push was
  created.
- 2026-08-26 DO synchronized `changerail-release-ci`, archived the same-slug
  change and moved this card to `3.inprogress` for one fresh ordinary/high
  review. Production/test/runtime LOC remains `0`; future authorization and
  successor cards/code remain absent.
- 2026-08-26T05:17:56Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
