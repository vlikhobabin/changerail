## Context

Connected broker v5 owns one Linux child tree and returns a closed bounded
result. Scheduler v1 must coordinate up to four such calls while staying
ignorant of Git selection, semantic inventory and release authority.

## Goals / Non-Goals

**Goals:**

- Validate the complete plan and reserve all roots before semantic launch.
- Provide exact-once jobs 1..4 execution with deterministic ordered results.
- Stop launching pending tasks after failure and preserve v5 cleanup for tasks
  already running.
- Fail closed on every malformed input, supervisor fault or malformed result.

**Non-Goals:**

- Do not select tasks or define the release semantic inventory.
- Do not activate baseline, CI, receipts, review/publish or profiles.
- Do not run history, full release baseline or live matrix evidence.

## Decisions

The implementation uses only this exact authorization reference:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-release-semantic-scheduler-v1.md","authorization_id":"authorize-bounded-release-semantic-scheduler-v1"}
```

### 1. Plan and result contracts are closed

`run_plan(plan, runtime_root, jobs, supervisor)` accepts a list of 1..64 exact
task objects. Every task contains only `id`, `command`, `execution_timeout`,
`cleanup_timeout` and one direct-child `root` name. IDs and roots are bounded
ASCII tokens; commands contain 1..64 bounded non-NUL arguments; timeouts are
finite positive values within v5 limits. All IDs, roots and resolved paths are
unique.

The scheduler reserves every root with exclusive `mkdir` before submitting
work. Any plan or reservation failure removes only empty roots created by that
attempt and launches zero semantic tasks.

Each task result contains only ID, status, reason, return code, output byte
count, cleanup flag and message count. Supervisor results must have the exact
v5 field set and cross-field consistency. The summary contains version,
overall status, jobs and registry-ordered results, is canonical JSON serializable
within 64 KiB and includes no child output.

### 2. Spawn workers coordinate public v5 calls

The production path uses a bounded `ProcessPoolExecutor` with the explicit
`spawn` multiprocessing context and 1..4 workers. Forking from a multithreaded
parent is forbidden. One manager-backed cross-process terminal event is passed
to every wrapper. Each wrapper checks it immediately before calling public v5
`supervise` and sets it after normalizing any terminal failure, before the
failure becomes visible to the parent. Wrappers not yet started return one
deterministic cancelled result. Already running v5 calls finish their own
cleanup. Results are collected by original plan index rather than completion
order. An activating entrypoint must call the scheduler under its guarded
`__main__` path so spawn never recursively executes scheduler setup.

The production default supervisor is imported from published
`changerail_release_child_broker`. Focused deterministic tests use a bounded
`ThreadPoolExecutor` only with an injected contract-equivalent supervisor, so
they can force event and executor lifecycle faults without replacing the real
production transport. Constructor, submit, wait and shutdown faults become one
complete ordered fail/cancelled result sequence; none escape as a partial
summary. Connected process tests use the real public v5 function.

### 3. Dormancy is structural

No production file except the scheduler module imports scheduler or broker for
scheduler activation. Focused proof scans all tracked Python, workflow and
entrypoint surfaces and allows scheduler imports only in its focused test.
Later exact affected-profile implementation is the sole permitted activation.

## Risks / Trade-offs

- **A terminal event cannot cancel a v5 call already running** -> only
  unstarted work is cancelled; running calls retain bounded v5 timeout and
  cleanup.
- **Root allocation is not a sandbox** -> it prevents collisions and gives each
  command an explicit reserved path; actual command arguments remain inventory
  ownership of the later profile.
- **Injected supervisor tests could become tautological** -> real-process
  timeout, output and descendant fixtures exercise the public v5 boundary.

## Migration Plan

1. Deliver and publish this dormant scheduler and proof.
2. Only then authorize affected-profile selection and sole activation.

## Open Questions

None. Selector mapping, inventory, CLI/report/receipt schemas and activation
belong to the affected-profile lineage.
