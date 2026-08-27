## ADDED Requirements

### Requirement: Affected v9 rescue MUST replace the terminal unpublished v8 contract
ChangeRail MUST publish
`rescue-affected-release-profile-direct-investigation-dependency-boundary-v9`
as one docs-only investigation/design decision from exact published
`authorize-bounded-affected-release-profile-v8` tip
`5b4981f92e55bec4644fef100171bb3e83f00cc1`.

The unpublished `implement-bounded-affected-release-profile-v8` lineage MUST be
terminal and forensic-only. Its card, code, tests, manifest, verdicts, logs,
evidence, preflight output and runtime files MUST NOT be read, copied,
cherry-picked, reproduced as chronology proof or accepted by a future gate.
The decision MAY retain only this concise chronology: v8 was clean-created
from published authorization; retained pre-production RED was valid;
focused/static/current checks passed; deterministic preflight blocked review
because direct-investigation dependency validation conflicts with the
published exact dependency set; semantic review and publish never ran.

Neither contract MAY be bypassed: v8 `Depends On` MUST NOT be mutated beyond
its published exact set, and the generic direct-investigation preflight MUST
NOT be weakened or treated as satisfied by a transitive dependency.

#### Scenario: Contradictory v8 contract stops before review
- **WHEN** executable v8 cannot both preserve its published exact dependency set and directly reference its investigation id
- **THEN** ChangeRail keeps v8 unpublished and forensic-only
- **AND** publishes a separate investigation/design decision before any replacement implementation exists.

### Requirement: Affected v9 rescue MUST authorize one directly bound clean lineage
The only future order MUST be this decision, docs-only
`authorize-bounded-affected-release-profile-v9`, clean
`implement-bounded-affected-release-profile-v9`, then
`certify-accelerated-release-loop-v1`.

The future authorization MUST contain exactly one object with only these fields
and values:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-direct-investigation-dependency-boundary-v9.md","investigation_id":"rescue-affected-release-profile-direct-investigation-dependency-boundary-v9","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v9.md","successor_id":"implement-bounded-affected-release-profile-v9","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Authorization v9 MUST depend exactly on this decision,
`decide-accelerated-release-loop-integration-boundary`,
`implement-bounded-release-semantic-scheduler-v1` and
`authorize-bounded-affected-release-profile-v8`, and MUST block only
implementation v9. The clean implementation MUST use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v9.md","authorization_id":"authorize-bounded-affected-release-profile-v9"}
```

Implementation v9 MUST depend exactly on this decision,
`decide-accelerated-release-loop-integration-boundary`,
`implement-bounded-release-semantic-scheduler-v1`,
`authorize-bounded-affected-release-profile-v8` and authorization v9. It MUST
block only certification, start from authorization-publishing HEAD and add at
most 499 production LOC. The direct dependency on this decision MUST satisfy
the same investigation id carried by the six-field object.

#### Scenario: Direct investigation edge and exact lineage agree
- **WHEN** maintainers preflight future implementation v9
- **THEN** its exact `Depends On` contains both this rescue investigation id and authorization v9
- **AND** no transitive predecessor is used to substitute the direct investigation edge.

### Requirement: Affected v9 rescue MUST preserve the accumulated release floor
Future v9 MUST preserve retained real pre-production RED: before production,
CI or main-spec mutation its captured command MUST print the workspace
fingerprint before a direct non-zero focused test, retain `status: failed`, a
non-zero exit, `tree_sha`, `diff_fingerprint` and a concrete missing
module/symbol error, keep the saved tree reachable and permit reconstruction
against exact authorization HEAD.

Future v9 MUST preserve the exact 35-ID digest and 35→30 ownership, one frozen
exhaustive typed registry, aggregate admission before Git/scheduler/filesystem
mutation, effective-interpreter `purelib`/`platlib` origins, strict bounded
committed/staged/unstaged/untracked NUL selection, typed scheduler-v1 sole
activation and closed rows, full-only publication authority, exact source-safe
four-step CI, closed import/call/raw-execution ownership, connected
source-mutant proof for every required guard and protocol-artifact
non-authority. Affected execution and its artifacts MUST remain developer
feedback and MUST NOT grant publication authority.

#### Scenario: Dependency repair does not weaken affected semantics
- **WHEN** authorization or implementation v9 is planned from this decision
- **THEN** the only changed boundary is the directly satisfiable investigation dependency
- **AND** all accumulated selection, admission, scheduling, authority, CI and proof requirements remain fail closed.

### Requirement: Affected v9 rescue MUST remain docs-only and dormant
This decision MUST modify only its card, same-slug OpenSpec artifacts,
synchronized `changerail-release-ci` main specification and archive metadata.
It MUST add production/test/runtime LOC `0`, create no authorization,
implementation or certification successor, and run or accept no reachable
history, real full baseline, affected execution/benchmark, live matrix or
certification evidence.

Certification MUST remain blocked until authorization v9 and clean
implementation v9 are separately reviewed, published and remotely reachable.

#### Scenario: Rescue changes lineage without activating release work
- **WHEN** maintainers plan, deliver, review or publish this decision
- **THEN** only docs/spec artifacts change while executable and successor surfaces remain absent
- **AND** certification remains blocked behind published implementation v9.
