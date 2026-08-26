# Design: bounded affected release profile v3 authorization

## Exact Source And Successor
The authorization starts from exact published decision commit
`8772376bc3b3bbb5d9aa2dd96c5a47c9430a863d` and repeats exactly:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-exact-target-proof-boundary.md","investigation_id":"rescue-affected-release-profile-exact-target-proof-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v3.md","successor_id":"implement-bounded-affected-release-profile-v3","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

It depends exactly on the source decision, integration decision, scheduler v1
and published v2 authorization and blocks only v3 implementation. The future
implementation uses only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v3.md","authorization_id":"authorize-bounded-affected-release-profile-v3"}
```

It starts from authorization-publishing HEAD, depends on those four predecessors
plus this authorization, blocks only certification and adds at most 499
production LOC.

## Preserved Boundary
The authorization preserves without reinterpretation the published 35→30
inventory, exact A/M/D and three-digit R/C grammar, closed executable/input-file/
input-directory/runtime-output descriptors, aggregate pre-semantic admission,
integer-only scheduler jobs and exact row tuples, affected non-authority,
full-only authority and literal four-step CI schema.

The future focused matrix must remain finite, exhaustive and connected to the
production guard for every selector stream/bound/fault, target mapping/kind/
root/type/access fault, scheduler typed cross-field/jobs mutation and CI field/
trigger/action/with/run/env/matrix/gating/direct/wrapped/indirect surface.

## Dormancy
This payload owns only docs/OpenSpec lineage. The implementation card/change,
profile, runner, CI mutation and evidence do not exist until authorization is
reviewed, committed, pushed and remotely reachable. Unpublished v2 artifacts
remain forbidden. History, real full, benchmark, live and certification work is
reserved for the later certification stage.
