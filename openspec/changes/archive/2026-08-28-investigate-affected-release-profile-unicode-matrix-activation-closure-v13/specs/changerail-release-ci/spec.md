## ADDED Requirements

### Requirement: Affected v13 investigation MUST replace terminal unpublished Unicode closure v12
ChangeRail MUST publish
`investigate-affected-release-profile-unicode-matrix-activation-closure-v13` as
one docs-only decision from exact safe published
`authorize-bounded-affected-release-profile-v11` commit
`9f72764e4969be9dcaebe08cabf06c6bbc9f4934`. The terminal unpublished v12
investigation MUST remain unpublished after review cycle 1 returned `9/14`
acceptance with three blockers, its sole bounded same-card rescue was consumed,
and cycle 2 returned `12/14` with two blockers and rescue budget `1/1/0`
exhausted. Only validated verdict summaries, counters and bounded conclusions
MAY cross the lineage boundary; v12 card, OpenSpec payload, manifest, verdicts,
logs and raw runtime evidence MUST NOT be read, copied, cherry-picked or
accepted.

The only successor order MUST be this investigation, docs-only
`authorize-bounded-affected-release-profile-v13`, clean
`implement-bounded-affected-release-profile-v13`, then
`certify-accelerated-release-loop-v1`. Before the authorization is published,
the v13 implementation card, focused test, production, CI and executable
main-spec mutations MUST remain absent. Future authorization MUST bind the
exact successor with a ceiling no greater than 500 production LOC, and future
implementation MUST add no more than 499 production LOC.

#### Scenario: Exhausted v12 is replaced without payload reuse
- **WHEN** maintainers inspect v13 lineage, changed paths and successor order
- **THEN** v12 chronology and exhausted `1/1/0` are preserved as concise summaries while terminal payload/evidence remain outside the lineage
- **AND** only the docs-only investigation exists before separately reviewed authorization and implementation successors.

### Requirement: Affected v13 RED MUST retain the exact contiguous missing-module exception line
Future v13 implementation MUST create a focused test that imports the genuinely
absent production module `changerail_release_affected_profile` and MUST directly
run it through `bin/changerail-evidence capture` before any production, CI or
main-spec mutation. The captured command MUST first print
`bin/changerail-review-verdict fingerprint --workspace .`, then execute the
focused test with a genuine non-zero exit and without `|| true`, an exit-zero
wrapper or substituted failure.

The retained raw output MUST contain one line exactly equal to
`ModuleNotFoundError: No module named 'changerail_release_affected_profile'`.
The oracle MUST compare the complete contiguous literal line; two fragment or
substring checks, reordered fragments, reconstructed prose and later
reproduction MUST NOT satisfy it. The same retained entry MUST bind
`status: failed`, the non-zero `exit_code`, exact exception line, `tree_sha` and
`diff_fingerprint`. Its saved tree object MUST exist before executable mutation
and MUST reconstruct relative to the authorization HEAD with no production, CI
or main-spec changes.

#### Scenario: Fragmented exception evidence fails closed
- **WHEN** retained RED output contains both expected substrings but not the exact contiguous exception line, or the line comes only from a later reproduction
- **THEN** RED chronology is unproven and review MUST fail closed.

#### Scenario: Exact pre-mutation RED remains reconstructable
- **WHEN** the original retained failed entry is audited against authorization HEAD
- **THEN** its raw output has the exact full exception line, non-zero exit and fingerprint fields
- **AND** its existing saved tree contains focused-test artifacts but no production, CI or main-spec mutation.

### Requirement: Affected v13 Unicode proof MUST use an independently authored oracle
Future v13 production MUST freeze Unicode 16.0.0 general categories `Cc|Cf` as
exactly 23 ordered non-overlapping ranges containing 235 code points with
canonical digest
`7fb5126f7973cc51a27f62c8712c11401ace15b9d40afdf02f1575945dc1da81`;
U+11F00 MUST remain a stable nonmember. The digest preimage MUST order ranges
by ascending start, encode each endpoint as exactly six uppercase ASCII
hexadecimal digits, encode each range as `START-END`, join records with one
ASCII semicolon and no whitespace, BOM, newline or trailing delimiter, and
apply SHA-256 to those ASCII/UTF-8 bytes.

The normative test oracle MUST own a separately authored literal dataset in a
different representation: the complete set of 235 scalar values sourced
directly from frozen Unicode 16.0.0 category data. Expected values MUST NOT be
generated, copied or derived from production ranges, production digest,
production iterator/helper or a shared production-derived intermediate
artifact. The oracle MUST NOT import production constants to construct its
expectation. It MUST independently derive contiguous boundaries, canonical
preimage bytes and digest from its test-owned scalar set, assert exact
range/count/digest and
U+11F00 nonmembership, and compare production membership for every member,
boundary neighbor and declared stable nonmember.

Missing, extra, split, merged or reordered ranges, category drift and a
production table whose matching digest repeats the same incorrect source MUST
all fail closed. Review MUST verify explicit independent authoring provenance
and absence of a data path from production table to oracle expectation.

#### Scenario: Production-derived oracle cannot self-certify Unicode inventory
- **WHEN** a test imports, copies or transforms production table/digest/helper output to build expected Unicode membership
- **THEN** independent-oracle acceptance fails even if all resulting assertions pass.

#### Scenario: Independent scalar oracle detects table drift
- **WHEN** one production boundary/member is missing, extra, split, merged, reordered or recategorized while production-local checks remain internally consistent
- **THEN** the separately authored 235-scalar oracle detects the mismatch and fails closed.

### Requirement: Affected v13 scheduler activation MUST be lexical, direct and connected
Future v13 `profile.main` MUST contain exactly one direct lexical-body statement
whose call expression invokes the unaliased imported name `run_plan`. The call
MUST NOT be nested in `if False`, `if True`, any other conditional expression,
loop, `try`, `with`, nested function, lambda or wrapper; it MUST NOT use an
alias, attribute, indirect callable or alternate activation call. No other
`run_plan` or scheduler activation call MAY exist in the module.

A structural oracle MUST verify the exact AST shape and a connected oracle MUST
load the actual public runner, profile and scheduler chain and observe the
required call through the public entrypoint. Missing, duplicate, nested,
guarded, wrapped, alternate, replacement or disconnected calls MUST fail
closed; tests MUST NOT replace production functions to manufacture reachability.

#### Scenario: Constant guard does not count as activation
- **WHEN** the only `run_plan` call is under `if True`, `if False` or another nested control-flow wrapper
- **THEN** lexical depth-one activation acceptance fails.

#### Scenario: Direct but disconnected call does not count as activation
- **WHEN** a direct call exists syntactically but the actual public runner chain cannot reach it
- **THEN** connected activation acceptance fails without a replacement production function.

### Requirement: Affected v13 investigation MUST preserve the accumulated affected floor without execution
The v13 decision MUST preserve the published v11 dedicated runtime-root,
read-only task-root pre-reservation and independently complete scheduler matrix.
It MUST also preserve the exact 35-ID digest and 35-to-30 typed ownership,
aggregate pre-mutation admission, effective `purelib`/`platlib` origins, strict
committed/staged/unstaged/untracked NUL selection, scheduler-v1 sole activation,
full-only publication authority, exact source-safe four-step CI, connected
resolved-base guard mutants and protocol-artifact non-authority.

This investigation MUST add zero production, test and runtime LOC and MUST
change only its board card, same-slug OpenSpec artifacts, synchronized
`changerail-release-ci` spec and archive metadata. It MUST NOT create v13
authorization/implementation or certification, and MUST NOT run or accept
reachable-history scan, real full baseline, affected execution/benchmark, live
matrix or certification evidence. One fresh `gpt-5.6-sol/high` ordinary review
MUST gate publication.

#### Scenario: Docs-only closure remains dormant
- **WHEN** maintainers audit changed paths, source classification and retained verification
- **THEN** production/test/runtime LOC are zero and executable successors are absent
- **AND** prohibited release, history, live and certification checks were neither run nor accepted.
