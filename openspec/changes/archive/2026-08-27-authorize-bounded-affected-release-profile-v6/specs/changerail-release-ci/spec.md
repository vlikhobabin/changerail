## ADDED Requirements

### Requirement: Affected v6 authorization MUST bind one exact implementation successor
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v6` as one
docs-only authorization from exact published
`rescue-affected-release-profile-admission-bounds-boundary-v6` commit
`5d6bfe14b498d22f58be303283537c16cd450c07`.

The authorization MUST contain exactly one object with only these fields and values:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-admission-bounds-boundary-v6.md","investigation_id":"rescue-affected-release-profile-admission-bounds-boundary-v6","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v6.md","successor_id":"implement-bounded-affected-release-profile-v6","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Its `Depends On` relation MUST contain exactly
`rescue-affected-release-profile-admission-bounds-boundary-v6`,
`decide-accelerated-release-loop-integration-boundary`,
`implement-bounded-release-semantic-scheduler-v1` and
`authorize-bounded-affected-release-profile-v5`. It MUST block only
`implement-bounded-affected-release-profile-v6`.

The future implementation MUST use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v6.md","authorization_id":"authorize-bounded-affected-release-profile-v6"}
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

### Requirement: Affected v6 authorization MUST require retained pre-production RED
Before any production, CI or main-spec mutation, future v6 MUST contain only its
card, same-slug OpenSpec and focused-test artifacts and MUST run its real failing
focused test through `bin/changerail-evidence capture`. The captured command
MUST first emit `bin/changerail-review-verdict fingerprint --workspace .` and
then run the test while preserving the test's non-zero exit status.

The retained entry MUST have `status: failed`, a non-zero `exit_code` and raw
output containing the pre-production `tree_sha`, `diff_fingerprint` and a
concrete absent production symbol/module error. The captured tree object MUST
remain reachable before production mutation. A zero-exit wrapper, synthetic
note, unsaved run or later reproduction MUST NOT satisfy test-first chronology.

The independent reviewer MUST reconstruct the retained Git tree object,
compare it against exact authorization HEAD and prove that production, CI and
main-spec paths were unchanged. Missing tree reachability, forbidden paths,
non-specific failure or post-production capture MUST fail closed.

#### Scenario: Authorization rejects unauditable RED chronology
- **WHEN** v6 requests review without a retained failing pre-production tree and specific missing-symbol/module error
- **THEN** the RED acceptance criterion fails
- **AND** later reproduction or a successful wrapper cannot repair that lineage.

### Requirement: Affected v6 authorization MUST bind admission before filesystem mutation
Future v6 MUST complete aggregate toolchain and runtime-output target admission
before Git selection, semantic scheduling and any `mkdir`, `mkdtemp`, file
creation or runtime-state mutation. The target leaf and nearest existing parent
MUST be bounded to real repository-local paths.

An absent leaf MAY pass only under a real non-symlink writable/searchable
repository-local directory. An existing leaf MAY pass only as a real
non-symlink writable/searchable directory. Existing file, symlink, other wrong
type, escaping, inaccessible or uncertain parent MUST emit a bounded aggregate
failure with `semantic_started: 0`; the CLI MUST NOT raise an uncaught exception
before that report.

Focused proof MUST reach each runtime-output fault through actual aggregate
admission and include a connected counterfactual that changes the exact
filesystem ordering or type guard.

#### Scenario: Existing runtime-output file fails before mutation
- **WHEN** the exact runtime-output target exists as a regular file before v6 starts
- **THEN** aggregate admission reports the target fault with `semantic_started: 0`
- **AND** no runtime directory, selector command or scheduler task starts.

### Requirement: Affected v6 authorization MUST require complete connected selector-bound proof
Future v6 MUST retain separate otherwise-valid happy/fault fixtures and non-noop
production-guard mutants for per-path `MAX_PATH`, aggregate/deduplicated
`MAX_PATHS`, each committed/staged/unstaged/untracked stream's
`MAX_GIT_BYTES`, aggregate four-stream `MAX_GIT_BYTES` and the runtime-output
ordering/type boundary.

Every named fault fixture MUST have valid Git/base/framing input apart from its
targeted bound and MUST reach the intended production guard. Removing or
weakening that exact guard MUST make the named fixture fail. Shared internal
helpers, disconnected duplicate logic, protocol artifacts or aggregate-only
success/failure assertions MUST NOT satisfy connected proof.

Future v6 MUST also preserve exact 35-ID digest and 35→30 ownership, aggregate
admission, strict bounded four-stream Git parsing, typed scheduler rows/jobs,
full-only authority, exact source-safe four-step CI, connected resolved-base
guards and protocol-artifact non-authority from published sources.

#### Scenario: Every selector bound owns one connected counterfactual
- **WHEN** maintainers disable or weaken any named path/count/stream/aggregate guard
- **THEN** its otherwise-valid focused fixture fails through the actual production path
- **AND** no different guard or protocol-artifact assertion can mask the defect.

### Requirement: Affected v6 authorization MUST remain docs-only and dormant
The authorization MUST modify only its card, same-slug OpenSpec artifacts,
synchronized `changerail-release-ci` specification and archive metadata. It
MUST add production/test/runtime LOC 0 and MUST NOT create successor cards,
tests, dependencies, schemas, code, CI, baseline, receipt or runtime authority.

Terminal unpublished v5 code, card, manifest, verdicts, logs and evidence MUST
NOT be read, copied, cherry-picked or accepted for implementation,
verification, review or publication. This authorization MUST NOT run or accept
reachable history, real full baseline, affected execution/benchmark, live
matrix, certification or terminal prototype evidence. It requires one fresh
Sol/high review and permits one same-card docs repair.

#### Scenario: Authorization cannot execute affected work
- **WHEN** maintainers plan, deliver, review or publish authorization
- **THEN** only exact lineage and future verification constraints change
- **AND** selector, scheduler, history, full, affected, live and certification work remains absent.
