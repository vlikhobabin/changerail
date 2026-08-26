# Зафиксировать connected-proof boundary для broker supervisor v5

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 02R11-S5

## Source
- Published broker decision `decide-brokered-release-child-supervision-boundary`,
  commit `163db9b0d77e3c5ba3a348901f45a69f02a6bbc6`.
- Published v4 authorization
  `authorize-bounded-brokered-release-child-supervisor-v4`, commit
  `4378a7b753abaf1fd4a355a0306ebc2933db1739`.
- Terminal unpublished v4 review findings R8/R9 are requirements input only;
  its code, card, verdict, history, manifest and evidence are not reused.

## Summary
Определить единственный clean v5 successor, в котором connected proof
доказывает outer cleanup и pidfd signaling через публичный `supervise`, а
counterfactual source mutations обязательно делают proof красным.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Future protocol scope: only the later exact authorization may permit the
  bounded v5 protocol reconstruction.
- Credential or mutation authority: `no`
- Live admission: `no`
- Final certification: `no`
- Independent review: one fresh `gpt-5.6-sol`/`high`
- Same-card repair budget limit/used/remaining: `1/0/1`, exhausted `false`

## Depends On
- `decide-brokered-release-child-supervision-boundary`
- `authorize-bounded-brokered-release-child-supervisor-v4`

## Blocks
- `authorize-bounded-connected-broker-supervisor-v5`
- `deliver-connected-broker-supervisor-v5`

## Acceptance
- The decision explicitly closes the unpublished v4 path and makes exact v5
  the sole conforming future broker-supervisor path.
- It freezes one exact future authorization object with ceiling `500` and
  protocol allowance `true`, plus the exact future two-field reference.

```json
{"investigation_card":"openspec/board/4.done/decide-connected-broker-supervisor-proof-boundary.md","investigation_id":"decide-connected-broker-supervisor-proof-boundary","successor_card":"openspec/board/3.inprogress/deliver-connected-broker-supervisor-v5.md","successor_id":"deliver-connected-broker-supervisor-v5","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-connected-broker-supervisor-v5.md","authorization_id":"authorize-bounded-connected-broker-supervisor-v5"}
```

- V5 starts from the future published authorization HEAD, adds at most `499`
  production LOC, adds no dependency and reconstructs code/tests without
  copying v4 payload or runtime evidence.
- R8 proof invokes only public `supervise`; deleting its fatal/timeout outer
  `_stop_group(proc)` wiring must make the connected test fail.
- R9 proof reaches signaling after identity validation; replacing
  `pidfd_send_signal` with `os.kill(pid, sig)` must make the connected test
  fail. A pre-signal mismatch rejection is insufficient.
- Both counterfactuals are executed in disposable source copies and produce
  retained bounded evidence; no direct private-helper test may substitute.
- V5 gets one implementation attempt and one fresh Sol/high review with
  repair/retry/rescue budget `0/0/0`.
- This decision remains docs-only and does not run or accept history, full
  release baseline, live matrix, v4 evidence or downstream activation.

## Change Set
- `decide-connected-broker-supervisor-proof-boundary`

## Verify
- GREEN: pre-archive strict target and post-sync strict capability/all OpenSpec
  validation.
- GREEN: exact lineage/object/proof-boundary and future-card-absence oracle.
- GREEN: JSON/TOML parse, source classification, current public-surface scan
  `1445/0`, tracked/untracked whitespace and diff checks.
- Production/test/runtime LOC `0`; future cards and executable payload absent.

## Archive
- `openspec/changes/archive/2026-08-26-decide-connected-broker-supervisor-proof-boundary/`

## Related
- `openspec/changes/decide-connected-broker-supervisor-proof-boundary/`
- `openspec/board/4.done/decide-brokered-release-child-supervision-boundary.md`
- `openspec/board/4.done/authorize-bounded-brokered-release-child-supervisor-v4.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
FF/DO completed: one docs-only decision defines exclusive v5 lineage and
mutation-sensitive connected proof. The synchronized change is archived and
awaits one fresh Sol/high review.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `decide-connected-broker-supervisor-proof-boundary`

### Why
V4 behavior passed targeted probes, but its final review correctly showed that
the committed tests did not observe the two decisive production connections.
The exhausted v4 lineage cannot be repaired or reused.

### Goal
Publish one docs-only replacement decision that authorizes a clean, mutation-
sensitive v5 proof boundary.

### Scope
- this card;
- same-slug OpenSpec artifacts;
- synchronized `changerail-release-ci` specification and archive metadata.

### Acceptance
- Exact v4 closure, v5 lineage, R8/R9 connected counterfactuals, clean-start,
  LOC, evidence, review and dormancy contracts are machine-checkable.

### Depends On
- `decide-brokered-release-child-supervision-boundary`
- `authorize-bounded-brokered-release-child-supervisor-v4`

### Related
- `openspec/changes/decide-connected-broker-supervisor-proof-boundary/`

## Log
- 2026-08-26 operator explicitly authorized a new separate card outside the
  exhausted v4 lineage; no v4 executable or runtime evidence was imported.
- 2026-08-26 FF created one apply-ready same-slug change; strict target/all
  OpenSpec, exact lineage/proof oracle, JSON/TOML, classification, current
  public scan and whitespace checks passed. No history/full/live work ran.
- 2026-08-26 DO synchronized five release-CI requirements, archived the
  same-slug change and retained production/test/runtime LOC `0`. No history,
  full baseline, live matrix, successor, review, commit or push ran.
- 2026-08-26T08:13:27Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
