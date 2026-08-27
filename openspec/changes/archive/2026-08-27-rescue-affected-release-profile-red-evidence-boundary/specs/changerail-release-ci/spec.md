## ADDED Requirements

### Requirement: RED-evidence rescue MUST replace terminal unpublished affected v4
ChangeRail MUST publish
`rescue-affected-release-profile-red-evidence-boundary` as one docs-only
decision from exact published `authorize-bounded-affected-release-profile-v4`
tip `3e85ce1de7e8b6f9bb60a04b924838e24064dd5b`.

The unpublished `implement-bounded-affected-release-profile-v4` path MUST be
terminal, non-conforming and forensic-only. Its code, card, manifest, verdicts,
logs and evidence MUST NOT be read, copied, cherry-picked or accepted for any
future dependency, authorization, implementation, review or publication gate.
After this decision is published, the v4 implementation successor MUST be
exhausted and superseded by the exclusive v5 lineage.

The only conforming order MUST be this decision, docs-only
`authorize-bounded-affected-release-profile-v5`, clean
`implement-bounded-affected-release-profile-v5`, then
`certify-accelerated-release-loop-v1`. The v5 authorization MUST contain exactly
one object with only these fields and values:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-red-evidence-boundary.md","investigation_id":"rescue-affected-release-profile-red-evidence-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v5.md","successor_id":"implement-bounded-affected-release-profile-v5","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Its `Depends On` relation MUST contain exactly
`rescue-affected-release-profile-red-evidence-boundary`,
`decide-accelerated-release-loop-integration-boundary`,
`implement-bounded-release-semantic-scheduler-v1` and
`authorize-bounded-affected-release-profile-v4`. It MUST block only
`implement-bounded-affected-release-profile-v5`.

The v5 implementation MUST use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v5.md","authorization_id":"authorize-bounded-affected-release-profile-v5"}
```

It MUST depend exactly on those four predecessors plus v5 authorization, block
only certification, start from the authorization-publishing HEAD, add at most
499 production LOC and reconstruct only from published sources.

#### Scenario: Rescue leaves one published-source successor path
- **WHEN** maintainers publish this decision
- **THEN** unpublished v4 is exhausted and exact v5 lineage is exclusive
- **AND** authorization, implementation and certification successors remain absent.

### Requirement: Affected v5 MUST retain auditable RED before production mutation
Before its first production, CI or main-spec mutation, v5 MUST contain only its
card, same-slug OpenSpec and focused-test artifacts and MUST invoke
`bin/changerail-evidence capture` with the real failing command. That command
MUST first emit the result of
`bin/changerail-review-verdict fingerprint --workspace .` and then run the
focused test while preserving its non-zero exit status.

The retained evidence entry MUST have `status: failed`, a non-zero `exit_code`
and raw output containing the pre-production `tree_sha`, `diff_fingerprint` and
a concrete error naming an absent production symbol or module. A wrapper that
returns zero, an unsaved terminal run, a synthetic note or a later reproduction
MUST NOT satisfy this boundary.

The independent reviewer MUST reconstruct the saved pre-production Git tree
object, compare it with the exact authorization HEAD and prove that no
production, CI or main-spec mutation existed. Missing or unreachable tree
objects, non-specific failures, forbidden paths or evidence captured after a
production mutation MUST fail closed.

#### Scenario: Saved failing tree proves test-first chronology
- **WHEN** v5 requests independent review after implementing the focused behavior
- **THEN** retained raw RED evidence binds a real non-zero missing-symbol/module failure to the saved pre-production tree
- **AND** tree reconstruction proves only card, OpenSpec and focused-test artifacts preceded production.

### Requirement: RED-evidence rescue MUST preserve the published affected v4 floor
V5 MUST preserve exact 35→30 ownership, aggregate admission before selection,
strict bounded four-stream Git parsing, typed scheduler rows/jobs, full-only
authority, exact source-safe four-step CI, every connected resolved-base guard
counterfactual and protocol-artifact non-authority. It MUST inherit these
requirements from published v4 sources and MUST NOT accept terminal v4 results
as implementation or evidence.

This decision MUST modify only its card, same-slug OpenSpec artifacts,
synchronized `changerail-release-ci` specification and archive metadata. It
MUST add production/test/runtime LOC 0 and MUST NOT create successor cards,
code, dependencies, schemas, CI or runtime authority.

It MUST NOT run or accept reachable history, real full baseline, affected
execution/benchmark, live matrix, certification or unpublished prototype
evidence. One fresh Sol/high review and one same-card docs repair are available.

#### Scenario: Decision cannot claim executable closure
- **WHEN** this decision is delivered or reviewed
- **THEN** only lineage and future RED-proof boundaries change
- **AND** executable closure remains absent until separately published v5 work.
