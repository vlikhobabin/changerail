## ADDED Requirements

### Requirement: Affected v11 authorization MUST bind one exact investigated successor
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v11` as one
docs-only authorization from exact published
`investigate-affected-release-profile-runtime-root-scheduler-matrix-v11`
commit `c1df80ff4591c6c2619856b91cc4e1bcdc50cec6`.

The authorization MUST contain exactly one object with only these fields and values:

```json
{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-runtime-root-scheduler-matrix-v11.md","investigation_id":"investigate-affected-release-profile-runtime-root-scheduler-matrix-v11","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v11.md","successor_id":"implement-bounded-affected-release-profile-v11","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Its `Depends On` relation MUST contain exactly
`investigate-affected-release-profile-runtime-root-scheduler-matrix-v11`,
`decide-accelerated-release-loop-integration-boundary`,
`implement-bounded-release-semantic-scheduler-v1` and
`authorize-bounded-affected-release-profile-v10`. It MUST block only
`implement-bounded-affected-release-profile-v11`.

The future implementation MUST use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v11.md","authorization_id":"authorize-bounded-affected-release-profile-v11"}
```

It MUST start from authorization-publishing HEAD, add at most 499 production
LOC, depend exactly on investigation v11, the integration decision, scheduler
v1, authorization v10 and this authorization, and block only
`certify-accelerated-release-loop-v1`. The investigation dependency MUST be
direct and its id MUST equal the six-field `investigation_id`. Implementation
card, change, focused tests and executable payload MUST remain absent until
this authorization is reviewed, committed, pushed and remotely reachable.

#### Scenario: Authorization leaves one exact successor absent
- **WHEN** maintainers deliver or review authorization v11
- **THEN** exact source object, dependencies, direct investigation edge and sole block are machine-checkable
- **AND** implementation v11 remains absent until authorization publication.

### Requirement: Affected v11 authorization MUST require retained pre-production RED
Before any production, CI or main-spec mutation, future v11 MUST contain only
its card, same-slug OpenSpec and focused-test artifacts and MUST run its real
failing focused test through `bin/changerail-evidence capture`. The captured
command MUST first emit `bin/changerail-review-verdict fingerprint --workspace
.` and then run the test while preserving its non-zero exit status.

The retained entry MUST have `status: failed`, a non-zero `exit_code` and raw
output containing pre-production `tree_sha`, `diff_fingerprint` and a concrete
absent production symbol/module error. The captured tree object MUST remain
reachable before production mutation. An independent reviewer MUST reconstruct
that tree against exact authorization HEAD and prove production, CI and
main-spec paths were unchanged. A zero-exit wrapper, synthetic note, unsaved
run or later reproduction MUST NOT satisfy chronology.

#### Scenario: Authorization rejects unauditable v11 RED chronology
- **WHEN** v11 requests review without a retained failing pre-production tree and concrete missing-symbol/module error
- **THEN** its RED acceptance fails
- **AND** late reproduction or a successful wrapper cannot repair the lineage.

### Requirement: Affected v11 authorization MUST preserve the accumulated and investigated floor
Future v11 MUST preserve exact 35-ID digest and 35→30 typed ownership, one
frozen exhaustive typed registry, aggregate admission before Git, scheduler or
filesystem mutation, effective-interpreter `purelib`/`platlib` origins and
strict bounded committed/staged/unstaged/untracked NUL selection.

Runtime-root admission MUST match the exact frozen repository-relative
dedicated target and reject empty, `.`, `..`, repository-root, NUL,
surrogate/non-encodable, overlong, absolute/multi-component/alternate,
lexically or really escaping, symlinked, wrong-type/access and non-dedicated
values before mutation. A missing leaf MAY pass only as the exact direct child
of its real non-symlink contained writable and searchable declared parent.

Every selected task root MUST receive one read-only pre-reservation proof for
exact bounded unique direct-child token, lexical/real containment and absence
of existing leaf, symlink or conflict before `run_plan`. Any aggregate fault
MUST return `semantic_started: 0`; race or atomic reservation failure MUST stay
bounded, non-authoritative and clean up only roots created by that attempt.

The independently authored normative requirement-to-row map and separate
immutable reason schema MUST cover every `completed`, terminal, outer,
synthetic and `cancelled` valid tuple; top-level version/jobs/status/size;
result identity/order/count; every allowed nullable/boolean alternative and
numeric lower/interior/upper neighbor; and one-field invalid type, bound and
cross-field cases for exact row fields.

The executable catalog MUST equal the independent required-row set in both
directions. Every row MUST bind a unique non-noop actual production-source or
AST mutant, valid canonical neighbor and public `profile.main` or `run_smoke`
observation after preceding guards pass. Missing, extra, duplicate or reused
rows; catalog-local self-validation; untested valid tuples; accepted
one-field mutants; replacement production functions; and masked, no-op,
disconnected or earlier-fault mutants MUST fail.

Future v11 MUST also preserve scheduler-v1 sole activation and closed typed
rows, full-only publication authority, exact source-safe four-step CI,
connected resolved-base guards, closed source ownership and protocol-artifact
non-authority. Affected execution and its artifacts MUST remain
non-authoritative developer feedback.

#### Scenario: Investigated boundaries preserve release authority
- **WHEN** future v11 is planned from this authorization
- **THEN** dedicated runtime-root, task pre-reservation and independent complete scheduler proof are additive to the accumulated floor
- **AND** all selection, scheduler, authority, CI and artifact contracts remain fail closed.

### Requirement: Affected v11 authorization MUST remain docs-only and dormant
This authorization MUST modify only its card, same-slug OpenSpec artifacts,
synchronized `changerail-release-ci` specification and archive metadata. It
MUST add production/test/runtime LOC `0` and MUST NOT create successor cards,
tests, dependencies, schemas, code, CI, baseline, receipt or runtime authority.

Terminal unpublished v10 card, code, tests, specs, manifest, verdicts, logs,
evidence, preflight output and runtime state MUST NOT be read, copied,
cherry-picked, reproduced or accepted. This authorization MUST NOT run or
accept reachable history, real full baseline, affected execution/benchmark,
live matrix or certification evidence.

#### Scenario: Authorization cannot execute affected work
- **WHEN** maintainers plan, deliver, review or publish authorization v11
- **THEN** only exact authorization and future verification constraints change
- **AND** implementation, history, full, affected, live and certification surfaces remain absent.
