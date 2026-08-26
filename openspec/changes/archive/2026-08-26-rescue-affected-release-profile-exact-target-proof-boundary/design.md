# Design: exact target/proof boundary для affected profile v3

## Clean Lineage
The decision starts from corrected published v2 authorization tip `042c68e`.
The unpublished v2 implementation card, code, manifest, verdicts, logs and
evidence are forensic-only and cannot satisfy any future gate. After this
decision is published the v2 implementation successor is exhausted and the only
future authorization repeats exactly:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-exact-target-proof-boundary.md","investigation_id":"rescue-affected-release-profile-exact-target-proof-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v3.md","successor_id":"implement-bounded-affected-release-profile-v3","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The implementation uses only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v3.md","authorization_id":"authorize-bounded-affected-release-profile-v3"}
```

Authorization and implementation dependency/sole-block relations are closed as
declared by the card. Implementation starts from the v3 authorization-publishing
HEAD and adds at most 499 production LOC.

## Exact Git Grammar
The three `git diff --name-status -z` streams accept only one-byte `A`, `M` or
`D`, or `R`/`C` followed by exactly three ASCII digits whose numeric value is in
`000..100`. R/C consume exactly old and new operands; A/M/D consume exactly one.
Unknown case, width, score, status, missing/extra operand, non-UTF-8/control/path
fault or aggregate bound violation selects the full inventory with one bounded
reason. The untracked stream remains NUL-framed paths only.

## Closed Target Inventory
The profile owns an immutable machine-readable descriptor for every frozen
command target. Each descriptor binds a command token/index to exactly one kind:
effective-PATH executable, repository input file, repository input directory or
runtime output. Repository inputs resolve within the root and match exact
regular-file/directory plus readable/searchable/executable access requirements.
Runtime outputs have an exact bounded repository-local parent and never count as
pre-existing inputs. Every non-option path target is mapped exactly once;
unknown, duplicate, missing, ambiguous, symlink escape, type/access mismatch or
unavailable target is an aggregate admission failure before selection/semantics.

## Exact Scheduler And CI Trust
Summary `jobs` has exact JSON integer type and equals requested `1` or `4`; bool,
float, string and null fail before authority. Existing exact field sets, result
order, row tuples, summary size and full-only authority remain unchanged.

Canonical CI remains the published exact four-step full-only workflow. Its
parsed oracle remains YAML-1.2-safe and exact for every top-level/job/step field,
literal action/with/run value and order.

## Connected Proof Matrix
Finite non-noop fixtures cover every Git stream plus base/nonancestor/stderr/
nonzero/timeout/framing/status/path/count/byte/self/unknown fallback; every
target descriptor kind and missing/duplicate/ambiguous/type/access/root fault;
every valid scheduler tuple plus valid-typed cross-field and jobs-type mutation;
and every exact CI field/name/trigger key+value/action/with/run/env/matrix/gating
surface including direct, chained, wrapped and indirect execution. Each fixture
must fail when its production guard is removed or weakened. No history, real
full, benchmark, live or certification evidence is allowed before certification.
