## ADDED Requirements

### Requirement: Affected v8 authorization MUST bind one exact implementation successor
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v8` as one
docs-only authorization from exact published
`investigate-affected-release-profile-contract-closure-boundary-v8` commit
`9e7631346ed70584ecc003ddead5f3b5ff9eedac`.

The authorization MUST contain exactly one object with only these fields and values:

```json
{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-contract-closure-boundary-v8.md","investigation_id":"investigate-affected-release-profile-contract-closure-boundary-v8","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v8.md","successor_id":"implement-bounded-affected-release-profile-v8","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Its `Depends On` relation MUST contain exactly
`investigate-affected-release-profile-contract-closure-boundary-v8`,
`decide-accelerated-release-loop-integration-boundary`,
`implement-bounded-release-semantic-scheduler-v1` and
`authorize-bounded-affected-release-profile-v7`. It MUST block only
`implement-bounded-affected-release-profile-v8`.

The future implementation MUST use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v8.md","authorization_id":"authorize-bounded-affected-release-profile-v8"}
```

It MUST start from authorization-publishing HEAD, add at most 499 production
LOC, depend exactly on
`rescue-affected-release-profile-installed-origin-boundary-v7`,
`decide-accelerated-release-loop-integration-boundary`,
`implement-bounded-release-semantic-scheduler-v1`,
`authorize-bounded-affected-release-profile-v6`,
`authorize-bounded-affected-release-profile-v7` and this authorization, and
block only `certify-accelerated-release-loop-v1`. Its card, change, focused
tests and executable payload MUST remain absent until this authorization is
committed, reviewed, pushed and remotely reachable.

#### Scenario: Authorization leaves one bounded v8 successor absent
- **WHEN** maintainers deliver or review this authorization
- **THEN** exact source object, dependencies, sole block and future reference are machine-checkable
- **AND** implementation v8 remains absent until authorization publication.

### Requirement: Affected v8 authorization MUST require retained pre-production RED
Before any production, CI or main-spec mutation, future v8 MUST contain only its
card, same-slug OpenSpec and focused-test artifacts and MUST run its real failing
focused test through `bin/changerail-evidence capture`. The captured command
MUST first emit `bin/changerail-review-verdict fingerprint --workspace .` and
then run the test while preserving the test's non-zero exit status.

The retained entry MUST have `status: failed`, a non-zero `exit_code` and raw
output containing the pre-production `tree_sha`, `diff_fingerprint` and a
concrete absent production symbol/module error. The captured tree object MUST
remain reachable before production mutation. A zero-exit wrapper, synthetic
note, unsaved run or later reproduction MUST NOT satisfy chronology.

The independent reviewer MUST reconstruct the retained Git tree object,
compare it against exact authorization HEAD and prove that production, CI and
main-spec paths were unchanged.

#### Scenario: Authorization rejects unauditable v8 RED chronology
- **WHEN** v8 requests review without a retained failing pre-production tree and specific missing-symbol/module error
- **THEN** the RED acceptance criterion fails
- **AND** later reproduction or a successful wrapper cannot repair that lineage.

### Requirement: Affected v8 authorization MUST require exhaustive typed admission
Future v8 MUST use one frozen immutable typed registry for all 30 physical tasks
and non-task targets. Every operand MUST have exactly one declared kind from
`executable`, `module`, `script`, `file`, `directory` and
`embedded-command`. Admission MUST independently extract every physical
operand and compare its typed multiset with the registry without suffix,
slash, existence or other path-shape inference.

Missing, extra, duplicate-ambiguous, repository-root, absolute, escaped,
symlink-substituted, wrong-type or wrong-kind operands MUST produce a bounded
fault with `semantic_started: 0` before Git selection, scheduler activation and
filesystem mutation. Exact runtime/dev pins and effective-interpreter
`purelib`/`platlib` origins MUST remain admitted fail closed.

#### Scenario: Every typed operand is admitted before semantics
- **WHEN** a future physical command adds, removes, embeds, duplicates or retypes an operand
- **THEN** aggregate admission detects the exact typed mismatch before any semantic or filesystem work begins.

### Requirement: Affected v8 authorization MUST close ownership and connected proof
Future v8 ownership oracle MUST bind exact unaliased imports to their loaded
names and authorized calls: one guarded runner profile `main`, one direct
profile scheduler `run_plan` and one direct scheduler broker activation.
Aliases, star/module imports, shadowing, rebinding, wrapping, attribute calls,
duplicate calls or calls outside the authorized guard/function MUST fail.

The oracle MUST maintain a closed raw execution-site inventory. Any additional
module-qualified call, individual semantic command, `subprocess`, `os.system`,
`exec`/`eval` or equivalent wrapper outside the typed scheduler chain MUST
fail, while canonical CI remains exactly four source-safe steps invoking only
the full runner.

Every required typed-target, origin, selector, runtime, scheduler, authority,
protocol-artifact and ownership/execution guard MUST have a passing canonical
neighbor and one bounded source/AST mutant of the actual production guard,
loaded in an isolated fixture and observed through the public runner/oracle
with preceding guards satisfied. Function/constant patching, local duplicate
assertions and earlier-fault masking MUST NOT satisfy proof.

#### Scenario: Canonical calls cannot hide alternate execution
- **WHEN** a mutant preserves canonical imports/calls but adds an alias, rebound binding, indirect execution or disconnected proof
- **THEN** the ownership or connected-proof gate fails before review handoff.

### Requirement: Affected v8 authorization MUST preserve the release floor and remain dormant
Future v8 MUST preserve exact 35-ID digest and 35→30 ownership, strict bounded
committed/staged/unstaged/untracked NUL selection, effective package origins,
aggregate pre-mutation admission, scheduler-v1 sole activation and closed typed
rows, full-only authority, exact source-safe four-step CI and protocol-artifact
non-authority.

This authorization MUST modify only its card, same-slug OpenSpec artifacts,
synchronized `changerail-release-ci` specification and archive metadata. It
MUST add production/test/runtime LOC `0` and MUST NOT create successor cards,
tests, dependencies, schemas, code, CI, baseline, receipt or runtime authority.

Terminal unpublished v7 code, card, manifest, verdicts, logs and evidence MUST
NOT be read, copied, cherry-picked or accepted for implementation,
verification, review or publication. This authorization MUST NOT run or accept
reachable history, real full baseline, affected execution/benchmark, live
matrix or certification evidence.

#### Scenario: Authorization cannot execute affected work
- **WHEN** maintainers plan, deliver, review or publish authorization v8
- **THEN** only exact lineage and future verification constraints change
- **AND** successor, selector, scheduler, history, full, affected, live and certification work remains absent.
