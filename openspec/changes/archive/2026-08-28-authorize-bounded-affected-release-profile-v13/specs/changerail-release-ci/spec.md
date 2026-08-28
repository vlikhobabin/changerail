## ADDED Requirements

### Requirement: Affected v13 authorization MUST bind one exact bounded successor
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v13` as one
docs-only authorization from exact published
`investigate-affected-release-profile-unicode-matrix-activation-closure-v13`
commit `1be1c2534c2d6553ad87532371ea852d2f2bd84b`. Before authorization mutation,
the remote investigation and authorization branches MUST both resolve to that
exact commit.

The authorization source MUST contain exactly this six-field object with no
additional keys, wrappers, alternate paths, ids, successor or ceiling:

`{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-unicode-matrix-activation-closure-v13.md","investigation_id":"investigate-affected-release-profile-unicode-matrix-activation-closure-v13","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v13.md","successor_id":"implement-bounded-affected-release-profile-v13","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`.

Authorization dependencies MUST be exactly investigation v13, the accelerated
release-loop integration decision, release semantic scheduler v1 implementation
and affected v11 authorization. It MUST block only
`implement-bounded-affected-release-profile-v13`.

Future implementation MUST use only
`{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v13.md","authorization_id":"authorize-bounded-affected-release-profile-v13"}`,
start from the authorization-publishing HEAD, add no more than 499 production
LOC, depend exactly on investigation v13, the integration decision, scheduler
v1, authorization v11 and this authorization, and block only
`certify-accelerated-release-loop-v1`.

#### Scenario: Exact authorization admits only implementation v13
- **WHEN** preflight resolves the published investigation, authorization object, successor reference, dependencies, block and LOC ceiling
- **THEN** only the exact clean implementation v13 successor is eligible
- **AND** any object/path/id/dependency/block/ceiling substitution fails closed.

### Requirement: Affected v13 authorization MUST preserve original line-exact RED chronology
Before any production, CI or main-spec mutation, future v13 MUST contain only
its implementation card, same-slug OpenSpec and focused-test artifacts. The
focused test MUST import the genuinely absent production module
`changerail_release_affected_profile` and MUST be run directly through
`bin/changerail-evidence capture`.

The captured command MUST first print
`bin/changerail-review-verdict fingerprint --workspace .`, then execute the
focused test with a genuine non-zero exit and without `|| true`, exit-zero
wrapper or substituted failure. One original retained entry MUST bind
`status: failed`, non-zero `exit_code`, `tree_sha`, `diff_fingerprint` and a raw
output line exactly equal to
`ModuleNotFoundError: No module named 'changerail_release_affected_profile'`.
Fragments, substring pairs, reordered fragments, reconstructed prose and later
reproduction MUST NOT satisfy chronology.

The captured tree object MUST exist before executable mutation. Independent
review MUST reconstruct it relative to exact authorization HEAD and prove that
production, CI and main-spec paths were unchanged.

#### Scenario: Inexact or late RED evidence fails closed
- **WHEN** the original retained entry lacks the exact contiguous exception line, genuine non-zero exit, fingerprint fields or existing pre-mutation tree
- **THEN** RED acceptance fails
- **AND** fragment matching, successful wrappers or later reproduction cannot repair chronology.

### Requirement: Affected v13 authorization MUST preserve independent Unicode and direct connected activation proofs
Future v13 MUST freeze Unicode 16.0.0 `Cc|Cf` as exactly 23 ordered
non-overlapping ranges containing 235 code points, with U+11F00 as a stable
nonmember and SHA-256 digest
`7fb5126f7973cc51a27f62c8712c11401ace15b9d40afdf02f1575945dc1da81`.
The digest preimage MUST order ranges by ascending start, encode each endpoint
as exactly six uppercase ASCII hexadecimal digits, encode each range as
`START-END`, join records with one ASCII semicolon and no whitespace, BOM,
newline or trailing delimiter, and hash those ASCII/UTF-8 bytes.

The normative oracle MUST own a separately authored test-only literal set of
all 235 scalar values sourced directly from frozen Unicode 16.0.0 category
data. Expectations MUST NOT be generated, copied or derived from production
ranges, digest, iterator/helper or a shared production-derived intermediate.
The oracle MUST independently derive boundaries, preimage bytes and digest,
then prove exact membership/nonmembership, ordering, non-overlap, counts,
digest, U+11F00 and boundary-neighbor/stable-nonmember behavior. Missing,
extra, split, merged, reordered or recategorized inventory MUST fail closed.

Future v13 `profile.main` MUST contain exactly one lexical direct-body statement
whose call expression invokes the unaliased imported `run_plan`. The call MUST
NOT be nested under constant or other conditionals, loops, `try`, `with`, nested
functions, lambdas or wrappers and MUST NOT use aliases, attributes, indirect
callables or alternate activation calls. Structural proof MUST be paired with a
connected observation through the actual public runner/profile/scheduler chain;
missing, duplicate, nested, guarded, wrapped, alternate, replacement or
disconnected calls MUST fail closed without replacement production functions.

#### Scenario: Independent Unicode and connected activation are additive gates
- **WHEN** future v13 is reviewed with internally consistent but production-derived Unicode expectations or a guarded/disconnected scheduler call
- **THEN** acceptance fails even if local production checks otherwise pass.

### Requirement: Affected v13 authorization MUST preserve the accumulated floor and remain dormant
Future v13 MUST preserve the published v11 exact dedicated runtime-root
admission, read-only task-root pre-reservation and independently complete
scheduler matrix. It MUST also preserve exact 35-ID digest and 35-to-30 typed
ownership, aggregate pre-mutation admission, effective `purelib`/`platlib`
origins, strict committed/staged/unstaged/untracked NUL selection, scheduler-v1
sole activation, full-only publication authority, exact source-safe four-step
CI, connected resolved-base guards and protocol-artifact non-authority.

Terminal unpublished v12 card, OpenSpec payload, manifest, verdicts, logs and
raw runtime evidence MUST NOT be read, copied, cherry-picked, reproduced or
accepted. Future v13 MUST be reconstructed only from published contracts after
remote publication of this authorization.

This authorization MUST add zero production, test and runtime LOC and MUST
change only its card, same-slug OpenSpec artifacts, synchronized
`changerail-release-ci` spec and archive metadata. It MUST NOT create the v13
implementation card, focused tests, production, CI or certification, and MUST
NOT run or accept reachable-history scan, real full baseline, affected
execution/benchmark, live matrix or certification evidence. One fresh
`gpt-5.6-sol/high` ordinary review MUST gate publication.

#### Scenario: Authorization remains docs-only and non-authoritative
- **WHEN** maintainers audit changed paths, successor absence and retained verification
- **THEN** production/test/runtime LOC are zero and executable successor surfaces remain absent
- **AND** affected execution/artifacts have no publication authority and prohibited checks were neither run nor accepted.
