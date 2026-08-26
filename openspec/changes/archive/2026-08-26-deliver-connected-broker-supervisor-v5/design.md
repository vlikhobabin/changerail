## Context

V5 starts from published authorization commit
`888f2aaeb5a5b352474c100c63c68f1de612a7a1`. Published requirements define a
dedicated Linux subreaper broker, bounded protocol and cleanup. The new proof
boundary additionally requires public-entrypoint counterfactuals for outer
process-group cleanup and pidfd signaling.

## Goals / Non-Goals

**Goals:**

- Implement a bounded broker/controller in at most 499 production LOC.
- Keep ownership inside a fresh broker subprocess that becomes subreaper before
  target launch.
- Fail closed on protocol, execution, identity, output and cleanup faults.
- Prove R8/R9 connections with effective disposable source mutations.

**Non-Goals:**

- Do not copy terminal v4 code or runtime evidence.
- Do not provide native Windows supervision.
- Do not activate release baseline, CI, receipts or downstream work.
- Do not run history, full baseline or live matrix evidence.

## Decisions

### 1. One module owns controller and broker roles

`supervise(command, execution_timeout, cleanup_timeout)` is the public API.
It launches the same module in broker mode in a new session and exchanges
newline-delimited closed JSON messages over bounded pipes. The broker enables
Linux subreaper mode before `ready`, then launches the target and owns only its
descendants.

### 2. Bounds are enforced while data is produced

Controller and broker use selector-driven incremental pipe reads. Message,
total stream, output and timeout bounds are finite and validated before launch.
EOF is stream state; completion requires a terminal report after target state
and cleanup.

### 3. Cleanup uses exact identities and pidfds

The broker discovers descendants through `/proc` and tracks `(pid,starttime)`.
Signals open a pidfd, revalidate identity and call `pidfd_send_signal`; PID-only
signaling is not used for owned targets. Cleanup performs bounded TERM/KILL,
wait/reap and two consecutive empty scans.

The controller owns only the broker session. Fatal loss or outer timeout calls
the exact outer `_stop_group(proc)` production wiring and returns failure.

### 4. Counterfactuals execute the public path

The focused suite copies the canonical source to a disposable directory,
performs one unique asserted mutation, imports that copy and invokes its public
`supervise` with the same scenario. Removing outer cleanup must expose a
surviving same-group target. Replacing pidfd signaling with `os.kill` must trip
the forbidden-backend observation after identity validation.

No test may call `_stop_group` directly to satisfy R8. R9 must reach signaling;
an earlier mismatch is not proof. Missing, duplicate or no-op mutation fails.

## Verification

- Focused canonical process/protocol/cleanup and R8/R9 mutation suite.
- Retained bounded evidence for the focused suite and static/current gates.
- Compile inventory, pinned Ruff, schemas, strict OpenSpec, classification,
  current public scan, JSON/TOML, whitespace, scope and preflight.

## Risks / Trade-offs

- Linux `/proc`, pidfd and subreaper APIs make this implementation Linux-only.
- Source counterfactuals are intentionally coupled to two critical constructs;
  a refactor must update proof deliberately rather than silently weakening it.
- `0/0/0` means any review defect terminates this implementation lineage.

## Migration Plan

1. Capture RED for missing module.
2. Implement module and canonical tests, then both effective counterfactuals.
3. Retain evidence, sync/archive, obtain one fresh Sol/high review.
4. Publish only on GO; activation remains a later change.

## Open Questions

None.
