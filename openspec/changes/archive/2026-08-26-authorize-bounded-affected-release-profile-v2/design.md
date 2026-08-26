# Design: bounded affected release profile v2 authorization

## Exact Source Object
This authorization is a docs-only successor of published decision commit
`64ba9ab5c3af79c3babc4800969a68eae20ec5bb` and repeats exactly:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-exact-report-proof-boundary.md","investigation_id":"rescue-affected-release-profile-exact-report-proof-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v2.md","successor_id":"implement-bounded-affected-release-profile-v2","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Its exact dependencies are the published decision, integration decision,
scheduler v1 implementation and affected v1 authorization. It blocks only
`implement-bounded-affected-release-profile-v2`.

## Future Implementation
The successor uses only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v2.md","authorization_id":"authorize-bounded-affected-release-profile-v2"}
```

It begins from authorization-publishing HEAD, adds at most 499 production LOC,
depends on those four predecessors plus this published authorization and blocks
only certification. Successor card/code remains absent until this authorization
is committed, reviewed, pushed and remotely reachable.

## Preserved Boundary
Authorization does not redefine implementation. It incorporates without
weakening the decision's exact registry/resolution, selector bounds, aggregate
admission order, scheduler summary/row status tuples, full-only authority,
receipt/capture/marker/cache non-authority, literal CI schema and exhaustive
connected counterfactual floor.

## Evidence Boundary
Only docs/static/current verification is permitted. Unpublished predecessor
payload/evidence, reachable history, full baseline, affected benchmark, live
matrix and certification cannot satisfy this authorization.
