## 1. Prove RED and Implement Closed Contracts

- [x] 1.1 Add focused smoke that fails because scheduler module is absent and
  covers plan/jobs/root/result validation.
- [x] 1.2 Implement complete prelaunch validation and exclusive root reservation.
- [x] 1.3 Implement jobs 1..4 exact-once dispatch through public v5 and ordered
  bounded result aggregation.
- [x] 1.4 Implement terminal-event cancellation and total supervisor/result
  fault conversion.

## 2. Prove Connected Behavior and Dormancy

- [x] 2.1 Cover jobs parity, exact once, completion reordering, root collision,
  malformed/duplicate/over-bound inputs and exact summary bound.
- [x] 2.2 Cover injected failure/exception/malformed result and assert pending
  tasks never call supervisor after terminal event.
- [x] 2.3 Cover real v5 normal, output overflow, timeout/protocol and descendant
  cleanup behavior with no survivor.
- [x] 2.4 Add repository-wide structural dormancy proof for baseline, CI,
  receipt, review/publish and other production entrypoints.

## 3. Verify and Archive Implementation

- [x] 3.1 Run focused smoke, pycompile inventory, pinned Ruff, schema/CI/runtime
  smokes, source classification and current public scan.
- [x] 3.2 Assert exact authorization, changed-path scope, successor absence,
  production LOC `<=499` and no activation/dependency drift.
- [x] 3.3 Validate target/capability/all OpenSpec, JSON/TOML, tracked/untracked
  whitespace, archive/main sync, manifest scope and ordinary/high preflight.
- [x] 3.4 Archive same-slug change, keep card `3.inprogress` and obtain one
  fresh Sol/high review before publish.
- [x] 3.5 Do not run history, full baseline, live matrix, affected successor or
  publish before fresh GO.
