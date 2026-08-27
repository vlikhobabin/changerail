## ADDED Requirements

### Requirement: Affected v5 authorization MUST bind one exact implementation successor
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v5` as one
docs-only authorization from exact published
`rescue-affected-release-profile-red-evidence-boundary` commit
`ab23b7c8cfafd1b031b669a9a07667e135efd603`.

The authorization MUST contain exactly one object with only these fields and values:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-red-evidence-boundary.md","investigation_id":"rescue-affected-release-profile-red-evidence-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v5.md","successor_id":"implement-bounded-affected-release-profile-v5","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Its `Depends On` relation MUST contain exactly
`rescue-affected-release-profile-red-evidence-boundary`,
`decide-accelerated-release-loop-integration-boundary`,
`implement-bounded-release-semantic-scheduler-v1` and
`authorize-bounded-affected-release-profile-v4`. It MUST block only
`implement-bounded-affected-release-profile-v5`.

The future implementation MUST use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v5.md","authorization_id":"authorize-bounded-affected-release-profile-v5"}
```

It MUST start from authorization-publishing HEAD, add at most 499 production
LOC, depend exactly on the four published predecessors above plus this
authorization and block only `certify-accelerated-release-loop-v1`. Its card,
change, focused tests and executable payload MUST remain absent until this
authorization is committed, reviewed, pushed and remotely reachable.

#### Scenario: Authorization leaves one bounded successor absent
- **WHEN** maintainers deliver or review this authorization
- **THEN** exact source object, dependencies, sole block and future reference are machine-checkable
- **AND** the implementation successor remains absent until publication.

### Requirement: Affected v5 authorization MUST require retained pre-production RED
Before any production, CI or main-spec mutation, future v5 MUST contain only its
card, same-slug OpenSpec and focused-test artifacts and MUST run its real failing
focused test through `bin/changerail-evidence capture`. The captured command
MUST first emit `bin/changerail-review-verdict fingerprint --workspace .` and
then run the test while preserving the test's non-zero exit status.

The retained entry MUST have `status: failed`, a non-zero `exit_code` and raw
output containing the pre-production `tree_sha`, `diff_fingerprint` and a
concrete absent production symbol/module error. A zero-exit wrapper, synthetic
note, unsaved run or later reproduction MUST NOT satisfy test-first chronology.

The independent reviewer MUST reconstruct the retained Git tree object, compare
it against the exact authorization HEAD and prove that production, CI and
main-spec paths were unchanged. Missing tree reachability, forbidden paths,
non-specific failure or post-production capture MUST fail closed.

#### Scenario: Authorization rejects unauditable RED chronology
- **WHEN** v5 requests review without a retained failing pre-production tree and specific missing-symbol/module error
- **THEN** the RED acceptance criterion fails
- **AND** later reproduction or a successful wrapper cannot repair that lineage.

### Requirement: Affected v5 authorization MUST preserve the published affected v4 floor
The future implementation MUST preserve exact 35-ID digest and 35→30 ownership,
aggregate admission before selection, strict bounded four-stream Git parsing,
typed scheduler rows/jobs, full-only authority, exact source-safe four-step CI,
connected resolved-base guards and protocol-artifact non-authority.

It MUST reconstruct from published sources. Terminal unpublished v4 code, card,
manifest, verdicts, logs and evidence MUST NOT be read, copied, cherry-picked or
accepted for implementation, verification, review or publication.

This authorization MUST modify only its card, same-slug OpenSpec artifacts,
synchronized `changerail-release-ci` specification and archive metadata. It
MUST add production/test/runtime LOC 0 and MUST NOT create successor cards,
tests, dependencies, schemas, code, CI, baseline, receipt or runtime authority.

It MUST NOT run or accept reachable history, real full baseline, affected
execution/benchmark, live matrix, certification or terminal prototype evidence.
It requires one fresh Sol/high review and permits one same-card docs repair.

#### Scenario: Authorization cannot execute affected work
- **WHEN** maintainers plan, deliver, review or publish authorization
- **THEN** only exact lineage and future verification constraints change
- **AND** selector, scheduler, history, full, affected, live and certification work remains absent.
