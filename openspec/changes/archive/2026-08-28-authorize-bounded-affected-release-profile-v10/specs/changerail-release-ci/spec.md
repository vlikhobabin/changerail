## ADDED Requirements

### Requirement: Affected v10 authorization MUST bind one exact rescued successor
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v10` as one
docs-only authorization from exact published
`rescue-affected-release-profile-runtime-containment-dynamic-execution-boundary-v10`
commit `0318483db897ade4908013e3d270bda60b0e1f3a`.

The authorization MUST contain exactly one object with only these fields and values:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-runtime-containment-dynamic-execution-boundary-v10.md","investigation_id":"rescue-affected-release-profile-runtime-containment-dynamic-execution-boundary-v10","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v10.md","successor_id":"implement-bounded-affected-release-profile-v10","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Its `Depends On` relation MUST contain exactly
`rescue-affected-release-profile-runtime-containment-dynamic-execution-boundary-v10`,
`decide-accelerated-release-loop-integration-boundary`,
`implement-bounded-release-semantic-scheduler-v1` and
`authorize-bounded-affected-release-profile-v9`. It MUST block only
`implement-bounded-affected-release-profile-v10`.

The future implementation MUST use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v10.md","authorization_id":"authorize-bounded-affected-release-profile-v10"}
```

It MUST start from authorization-publishing HEAD, add at most 499 production
LOC, depend exactly on the rescue decision, integration decision, scheduler v1,
authorization v9 and this authorization, and block only
`certify-accelerated-release-loop-v1`. The rescue dependency MUST be direct and
its id MUST equal the six-field `investigation_id`. Implementation card,
change, focused tests and executable payload MUST remain absent until this
authorization is reviewed, committed, pushed and remotely reachable.

#### Scenario: Authorization leaves one exact successor absent
- **WHEN** maintainers deliver or review authorization v10
- **THEN** exact source object, dependencies, direct rescue edge and sole block are machine-checkable
- **AND** implementation v10 remains absent until authorization publication.

### Requirement: Affected v10 authorization MUST require retained pre-production RED
Before any production, CI or main-spec mutation, future v10 MUST contain only
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

#### Scenario: Authorization rejects unauditable v10 RED chronology
- **WHEN** v10 requests review without a retained failing pre-production tree and concrete missing-symbol/module error
- **THEN** its RED acceptance fails
- **AND** late reproduction or a successful wrapper cannot repair the lineage.

### Requirement: Affected v10 authorization MUST preserve the accumulated and rescued floor
Future v10 MUST preserve exact 35-ID digest and 35→30 typed ownership, one
frozen exhaustive typed registry, aggregate admission before Git, scheduler or
filesystem mutation, effective-interpreter `purelib`/`platlib` origins and
strict bounded committed/staged/unstaged/untracked NUL selection.

Runtime-output admission MUST validate the resolved repository root, every
existing ancestor and the leaf, rejecting symlinked components, lexical or
resolved escape, wrong type and insufficient access before mutation. Source
ownership MUST compare the exact normalized inventory of every import and
every `ast.Call` in runner, profile and scheduler scopes and reject alternate
or dynamic execution even when the canonical direct chain remains.

The immutable normative guard catalog MUST cover every target, origin,
runtime, selector, scheduler, authority, artifact and ownership guard. Every
row MUST bind a unique id, passing canonical neighbor, one non-noop
actual-source/AST mutant, public `profile.main` or `run_smoke` observation and
evidence that preceding guards passed. Runtime replacement of production
functions, private-helper-only observation, reused mutants and earlier-fault
masking MUST fail.

Future v10 MUST also preserve scheduler-v1 sole activation and closed typed
rows, full-only publication authority, exact source-safe four-step CI and
protocol-artifact non-authority. Affected execution and its artifacts MUST
remain non-authoritative developer feedback.

#### Scenario: Rescued boundaries preserve release authority
- **WHEN** future v10 is planned from this authorization
- **THEN** runtime containment, closed execution ownership and complete connected proof are additive to the accumulated floor
- **AND** all selection, scheduler, authority, CI and artifact contracts remain fail closed.

### Requirement: Affected v10 authorization MUST remain docs-only and dormant
This authorization MUST modify only its card, same-slug OpenSpec artifacts,
synchronized `changerail-release-ci` specification and archive metadata. It
MUST add production/test/runtime LOC `0` and MUST NOT create successor cards,
tests, dependencies, schemas, code, CI, baseline, receipt or runtime authority.

Terminal unpublished v9 card, code, tests, specs, manifest, verdicts, logs,
evidence, preflight output and runtime state MUST NOT be read, copied,
cherry-picked, reproduced or accepted. This authorization MUST NOT run or
accept reachable history, real full baseline, affected execution/benchmark,
live matrix or certification evidence.

#### Scenario: Authorization cannot execute affected work
- **WHEN** maintainers plan, deliver, review or publish authorization v10
- **THEN** only exact lineage and future verification constraints change
- **AND** implementation, history, full, affected, live and certification surfaces remain absent.
