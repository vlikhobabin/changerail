# Design: proof-connectivity boundary для affected profile v4

## Clean Lineage
The decision starts from published v3 authorization tip `4203d1d`. The
unpublished v3 implementation card, code, manifest, verdicts, logs and evidence
are forensic-only and cannot satisfy any future gate. After this decision is
published the v3 implementation successor is exhausted. The only future
authorization repeats exactly:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-proof-connectivity-boundary.md","investigation_id":"rescue-affected-release-profile-proof-connectivity-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v4.md","successor_id":"implement-bounded-affected-release-profile-v4","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The implementation uses only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v4.md","authorization_id":"authorize-bounded-affected-release-profile-v4"}
```

Authorization and implementation dependency/sole-block relations are closed as
declared by the card. Implementation starts from the v4 authorization-publishing
HEAD and adds at most 499 production LOC.

## Resolved-Base Mutation Oracle
The v4 focused proof reaches resolved-base validation with an otherwise valid
probe and independently varies spawn/error, nonzero return, stderr, timeout,
single-newline framing, OID width and lowercase-hex grammar. Exact 40- and
64-byte lowercase OIDs pass; uppercase, non-hex, short, long, missing newline,
multiple newline and trailing bytes fail closed. Non-ancestor is tested only
after one valid resolved OID. Counterfactual source or injected-guard mutants
remove each condition independently and MUST make at least one named fixture fail.

## Protocol Non-Authority Oracle
Fixtures establish five non-authoritative starting states: affected subset,
affected full fallback, admission failure, scheduler failure and malformed
scheduler summary. For each state and each receipt, capture, marker and cache
class, the fixture adds, forges and replays a repository-local disposable
artifact. Authority, exit/report semantics, selected/result identities and
semantic-start counts remain exactly those of the artifact-free control. No
protocol field is emitted and no artifact is read, accepted, created or updated.
An explicit mutant that OR-upgrades authority from artifact presence MUST fail.

## Preserved Trust Floor
V4 changes no published broker/scheduler supervision. It preserves exact 35
semantic IDs, 30 physical tasks, aggregate admission before selection, strict
committed/staged/unstaged/untracked parsing and bounds, typed scheduler summary
validation, full-only authority, protocol absence and exact source-safe
four-step CI. Focused/static/current proof remains the only pre-certification
evidence; history, real full, affected execution/benchmark, live matrix and
certification remain prohibited.
