# Design: bounded affected release profile v4 authorization

## Exact Source And Successor
The authorization starts from exact published decision commit
`63be8754ed6deb474d1c91dab3e931d28e7f37d3` and repeats exactly:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-proof-connectivity-boundary.md","investigation_id":"rescue-affected-release-profile-proof-connectivity-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v4.md","successor_id":"implement-bounded-affected-release-profile-v4","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

It depends exactly on the source decision, integration decision, scheduler v1
and published v3 authorization and blocks only v4 implementation. The future
implementation uses only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v4.md","authorization_id":"authorize-bounded-affected-release-profile-v4"}
```

It starts from authorization-publishing HEAD, depends on those four predecessors
plus this authorization, blocks only certification and adds at most 499
production LOC.

## Preserved Proof Connectivity
The future implementation must reach every resolved-base validation guard with
an otherwise valid probe. It independently mutates error, return code, stderr,
timeout, exact single-newline framing, 40/64-byte lowercase hexadecimal OID,
upper/non-hex/short/long/multiple/missing-newline and non-ancestor after valid
resolution. Removing or weakening any one guard makes a named fixture fail.

Protocol fixtures start from five non-authoritative controls: affected subset,
affected full fallback, admission failure, scheduler failure and malformed
summary. Add, forge and replay of each receipt/capture/marker/cache class keeps
authority, status, selection/results and semantic-start counts exactly equal to
the artifact-free control. An explicit artifact-presence authority mutant fails.

## Preserved Runtime Boundary
The authorization preserves without reinterpretation exact 35→30 ownership,
aggregate admission, strict committed/staged/unstaged/untracked parsing and
bounds, typed scheduler summary validation, full-only authority and exact
source-safe four-step CI. It owns no implementation, dependency, protocol or
runtime state. Unpublished v3 artifacts remain forbidden. History, real full,
affected execution/benchmark, live and certification work remains reserved for
the later certification stage.
