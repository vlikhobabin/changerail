# Спасти release authority через two-stage boundary

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 02R7-I

## Source
- Published split rescue `rescue-tiered-release-verification-split-boundary`,
  commit `25f756e`.
- Published broad Scope A authorization
  `authorize-bounded-tiered-release-authority-core`, commit `0fba407`.
- Recovery for unpublished `implement-tiered-release-authority-core`, whose
  pre-capture audit was NO-GO. Its payload remains forensic-only and is not
  committed, pushed or reused.

## Summary
Разделить Scope A на dormant passive admission/registry library A1 и отдельную
terminal authority activation A2. A1 получает релевантный focused proof без
бесполезного full baseline; A2 единственная активирует release authority и
выполняет atomic terminal gate.

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Planning: fresh `gpt-5.6-sol`/`high`
- Implementation: fresh `gpt-5.6-terra`/`high`
- Independent review: fresh `gpt-5.6-sol`/`xhigh`
- Same-card repair: at most one fresh `gpt-5.6-terra`/`high`
- Re-review: fresh `gpt-5.6-sol`/`xhigh`
- Same-card repair/rescue budget limit/used/remaining: `1/1/0`, exhausted `true`

## Depends On
- `rescue-tiered-release-verification-split-boundary`
- `authorize-bounded-tiered-release-authority-core`

## Blocks
- `authorize-bounded-passive-release-admission-registry`
- `implement-passive-release-admission-registry`
- `authorize-bounded-terminal-release-authority-activation`
- `implement-terminal-release-authority-activation`
- `authorize-clean-git-compatible-structural-history-scan-v2`
- `deliver-clean-git-compatible-structural-history-scan-v2`
- `authorize-bounded-windows-release-matrix-scheduler`
- `implement-bounded-windows-release-matrix-scheduler`
- `authorize-bounded-parallel-verify-project-cases`
- `parallelize-isolated-verify-project-cases`
- `parallelize-isolated-release-smoke-cases`

## Acceptance
- A1 owns exact literal 35-record registry/digest/owners/commands/groups, total
  bounded injected admission, effective-PATH Python and parsed pins/Ruff origin,
  offline OpenSpec, bounded Git A/M/D/R/C/untracked selector, closed path map,
  AST ownership oracle and connected faults.
- До публикации exact A2 A1 structurally dormant: baseline, CI,
  manifest/review/pub preflight, receipt schemas and production entrypoints
  cannot import, invoke or activate it. После публикации A2 только exact A2
  может import/invoke/activate published A1; negative-wiring oracle делает RED
  любую activation path до A2 или вне exact A2.
- A1 exact authorization uses ceiling `500`, protocol `false`; implementation
  `<=499` vs its published auth HEAD. Its exact object is
  `{"investigation_card":"openspec/board/4.done/rescue-tiered-release-authority-two-stage-boundary.md","investigation_id":"rescue-tiered-release-authority-two-stage-boundary","successor_card":"openspec/board/3.inprogress/implement-passive-release-admission-registry.md","successor_id":"implement-passive-release-admission-registry","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":false}`.
- A1 publication gate принимает только real offline admission и
  focused/static/current deterministic proof перед fresh Sol/xhigh review. A1
  MUST NOT execute, require or accept history scan, full baseline, authority
  receipt или terminal capture.
- A2 exclusively imports published A1 and owns pre-admission reservation,
  O_EXCL/held lock/directory fsync, bounded append-only JSONL, atomic terminal
  publication, signal terminalization, strict receipt/marker/manifest equality,
  required review/pub gate, canonical CI activation and parsed YAML oracle.
- A2 exact authorization uses ceiling `500`, protocol `true`; implementation
  `<=499` vs its published auth HEAD. Its exact object is
  `{"investigation_card":"openspec/board/4.done/rescue-tiered-release-authority-two-stage-boundary.md","investigation_id":"rescue-tiered-release-authority-two-stage-boundary","successor_card":"openspec/board/3.inprogress/implement-terminal-release-authority-activation.md","successor_id":"implement-terminal-release-authority-activation","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`.
- A2 uses capture ID
  `implement-terminal-release-authority-activation-cycle-1`, pre-capture audit
  and terminal/review budget `0/0/0`.
- Required remote-reachable order is A1 authorization/implementation, A2
  authorization/implementation, clean scanner-v2 authorization/implementation,
  Windows scheduler authorization/implementation, verify-project authorization/
  implementation, then the separate review-preflight and delivery-runner smoke
  successor.
- Windows scheduler, scanner, verify-project and release-smoke scopes remain
  separate downstream lineages. Docs-only decision production/test/runtime LOC
  0; no history/baseline.

## Change Set
- `rescue-tiered-release-authority-two-stage-boundary`

## Verify
- Strict OpenSpec, exact A1/A2 objects/ownership/dormancy/order, current public
  scan, JSON/TOML/classification/diff/scope/preflight.
- No history scan or full baseline.

## Result
DO complete: one docs-only rescue change was synced and archived for review
handoff. A1/A2 ownership, exact authorization objects, dormancy and immutable
downstream order are constrained without executable LOC.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Related
- `openspec/changes/archive/2026-08-25-rescue-tiered-release-authority-two-stage-boundary/`
- `openspec/board/4.done/rescue-tiered-release-verification-split-boundary.md`
- `openspec/board/4.done/authorize-bounded-tiered-release-authority-core.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Change 1: `rescue-tiered-release-authority-two-stage-boundary`

### Why
Broad Scope A combined dormant parsing/admission with terminal activation and
could not prove both inside one bounded implementation.

### Scope
- Decision/card/release-CI contract only; executable LOC 0.

### Acceptance
- Exact A1/A2 six-field objects use independent ceiling `500` and protocol
  flags `false`/`true`; each future implementation remains `<=499` against its
  own published authorization HEAD.
- A1 remains dormant through publication of A2; thereafter only exact A2 may
  activate it. A1 publication admits only offline/focused/static/current proof
  and MUST NOT execute, require or accept history/full/receipt/capture. A2
  alone activates terminal authority through one audited atomic capture and
  budget `0/0/0`.
- Published `25f756e` and `0fba407` are the only sources; failed Scope A remains
  forensic-only, while every downstream lineage follows exact publication
  order without ownership overlap.

### Depends On
- `rescue-tiered-release-verification-split-boundary`
- `authorize-bounded-tiered-release-authority-core`

### Related
- `openspec/changes/rescue-tiered-release-authority-two-stage-boundary/`

## Log
- Two-stage rescue was created after Scope A pre-capture NO-GO; failed payload
  remains forensic-only.
- FF prepared exactly one apply-ready same-slug docs-only rescue change with
  exact A1/A2 objects, passive dormancy, A1 focused-only proof, A2 atomic
  one-shot authority and immutable downstream order. No failed implementation
  payload, successor, main-spec sync, history/full baseline, archive, review,
  commit or push was created at that handoff.
- DO then synchronized and archived the docs-only change before independent
  review handoff; no executable successor, history/full baseline, review,
  commit or push was run.
- Cycle-1 independent review returned NO-GO for R1-R3. This same-card repair
  makes A1 dormancy time-bounded, makes the A1 publication gate exclusive and
  removes invented timestamps. The ignored manifest remains pending the fresh
  cycle-2 preflight and review.
- 2026-08-25T10:32:22Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
