## ADDED Requirements

### Requirement: Affected v9 authorization MUST bind one exact directly investigated successor
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v9` as one
docs-only authorization from exact published
`rescue-affected-release-profile-direct-investigation-dependency-boundary-v9`
commit `ab8e9a5391fc9be6a5e2c1a2f8ffad9202626c6f`.

The authorization MUST contain exactly one object with only these fields and values:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-direct-investigation-dependency-boundary-v9.md","investigation_id":"rescue-affected-release-profile-direct-investigation-dependency-boundary-v9","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v9.md","successor_id":"implement-bounded-affected-release-profile-v9","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Its `Depends On` relation MUST contain exactly
`rescue-affected-release-profile-direct-investigation-dependency-boundary-v9`,
`decide-accelerated-release-loop-integration-boundary`,
`implement-bounded-release-semantic-scheduler-v1` and
`authorize-bounded-affected-release-profile-v8`. It MUST block only
`implement-bounded-affected-release-profile-v9`.

The future implementation MUST use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v9.md","authorization_id":"authorize-bounded-affected-release-profile-v9"}
```

It MUST start from authorization-publishing HEAD, add at most 499 production
LOC, depend exactly on the rescue decision, integration decision, scheduler v1,
authorization v8 and this authorization, and block only
`certify-accelerated-release-loop-v1`. The rescue dependency MUST be direct and
its id MUST equal the six-field `investigation_id`. Implementation card,
change, focused tests and executable payload MUST remain absent until this
authorization is reviewed, committed, pushed and remotely reachable.

#### Scenario: Authorization leaves one directly bound successor absent
- **WHEN** maintainers deliver or review authorization v9
- **THEN** exact source object, dependencies, direct investigation edge and sole block are machine-checkable
- **AND** implementation v9 remains absent until authorization publication.

### Requirement: Affected v9 authorization MUST require retained pre-production RED
Before any production, CI or main-spec mutation, future v9 MUST contain only its
card, same-slug OpenSpec and focused-test artifacts and MUST run its real failing
focused test through `bin/changerail-evidence capture`. The captured command
MUST first emit `bin/changerail-review-verdict fingerprint --workspace .` and
then run the test while preserving its non-zero exit status.

The retained entry MUST have `status: failed`, a non-zero `exit_code` and raw
output containing pre-production `tree_sha`, `diff_fingerprint` and a concrete
absent production symbol/module error. The captured tree object MUST remain
reachable before production mutation. An independent reviewer MUST reconstruct
that tree against exact authorization HEAD and prove production, CI and
main-spec paths were unchanged. A zero-exit wrapper, synthetic note, unsaved
run or later reproduction MUST NOT satisfy chronology.

#### Scenario: Authorization rejects unauditable v9 RED chronology
- **WHEN** v9 requests review without a retained failing pre-production tree and concrete missing-symbol/module error
- **THEN** its RED acceptance fails
- **AND** late reproduction or a successful wrapper cannot repair the lineage.

### Requirement: Affected v9 authorization MUST preserve the accumulated affected floor
Future v9 MUST preserve exact 35-ID digest and 35→30 ownership, one frozen
exhaustive typed registry, aggregate admission before Git, scheduler or
filesystem mutation, effective-interpreter `purelib`/`platlib` origins and
strict bounded committed/staged/unstaged/untracked NUL selection.

It MUST preserve scheduler-v1 sole activation and closed typed rows, full-only
publication authority, exact source-safe four-step CI, closed
import/call/raw-execution ownership, connected source-mutant proof for every
required target/origin/selector/runtime/scheduler/authority/artifact/ownership
guard and protocol-artifact non-authority. Affected execution and its artifacts
MUST remain non-authoritative developer feedback.

The future implementation MUST satisfy the generic direct-investigation gate
with its direct rescue dependency. A transitive rescue reference MUST NOT
substitute that edge, and neither generic preflight nor published v8 contracts
MAY be weakened.

#### Scenario: Direct dependency repair preserves runtime semantics
- **WHEN** future v9 is planned from this authorization
- **THEN** only the dependency boundary differs from terminal v8
- **AND** all selection, admission, scheduler, authority, CI and proof contracts remain fail closed.

### Requirement: Affected v9 authorization MUST remain docs-only and dormant
This authorization MUST modify only its card, same-slug OpenSpec artifacts,
synchronized `changerail-release-ci` specification and archive metadata. It
MUST add production/test/runtime LOC `0` and MUST NOT create successor cards,
tests, dependencies, schemas, code, CI, baseline, receipt or runtime authority.

Terminal unpublished v8 card, code, tests, manifest, verdicts, logs, evidence,
preflight output and runtime state MUST NOT be read, copied, cherry-picked,
reproduced or accepted. This authorization MUST NOT run or accept reachable
history, real full baseline, affected execution/benchmark, live matrix or
certification evidence.

#### Scenario: Authorization cannot execute affected work
- **WHEN** maintainers plan, deliver, review or publish authorization v9
- **THEN** only exact lineage and future verification constraints change
- **AND** implementation, history, full, affected, live and certification surfaces remain absent.
