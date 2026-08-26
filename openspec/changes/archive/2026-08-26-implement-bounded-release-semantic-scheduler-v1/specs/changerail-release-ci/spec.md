## ADDED Requirements

### Requirement: Scheduler v1 MUST execute bounded plans deterministically
`implement-bounded-release-semantic-scheduler-v1` MUST start from published
authorization HEAD `ad6fa60cd641838cbef31059245e8cee9cbaa601`, use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-release-semantic-scheduler-v1.md","authorization_id":"authorize-bounded-release-semantic-scheduler-v1"}
```

and add at most 499 production LOC with no dependency. It MUST import only
published connected broker v5 for child ownership.

The scheduler MUST validate one closed immutable plan of 1..64 unique bounded
task IDs, commands, execution/cleanup timeouts and direct-child root names. It
MUST reserve all unique isolated roots before semantic launch and MUST launch
zero tasks on any validation or allocation failure.

Jobs MUST be an integer 1..4. Each started task MUST invoke public v5
`supervise` exactly once. Jobs 1 and default parallel execution MUST return the
same exact-once deterministic registry-ordered result sequence for equivalent
task outcomes.

The production path MUST use a `ProcessPoolExecutor` with explicit
multiprocessing `spawn`, never fork, and one manager-backed process-safe
terminal event shared by every worker wrapper. Each wrapper MUST set the event
after normalizing a failure and before returning it. A later activating
entrypoint MUST call the scheduler only under a guarded `__main__` path.
Focused deterministic proof MAY use a bounded thread executor only with an
injected supervisor. Constructor, submit, wait and shutdown faults MUST become
one complete ordered fail/cancelled result sequence and MUST NOT escape as a
partial result.

#### Scenario: Prevalidation reserves all roots before execution
- **WHEN** a plan contains malformed, duplicate, over-bound or colliding input
- **THEN** scheduler returns or raises a bounded validation failure before any
  supervisor call
- **AND** it removes only empty roots created by the failed reservation attempt.

#### Scenario: Parallel completion retains registry order
- **WHEN** valid independent tasks complete in different orders under jobs 1
  and jobs 4
- **THEN** every task executes exactly once and both summaries retain original
  plan order
- **AND** each result has the exact closed bounded field set.

### Requirement: Scheduler v1 MUST fail fast without bypassing v5 cleanup
Scheduler MUST set one shared terminal event after the first terminal task
failure, supervisor exception or malformed supervisor result. Tasks not yet
started MUST NOT call
the supervisor and MUST receive one deterministic cancelled result. Already
running tasks MUST finish through public v5 bounded cleanup before scheduler
returns.

Every child MUST retain the v5 8192-byte combined-output cap. Scheduler summary
MUST be canonical JSON serializable, at most 64 KiB and contain no raw output.
Malformed, duplicate, missing, unknown, incomplete or cross-field-invalid
result state MUST fail closed.

#### Scenario: First failure cancels unstarted tasks
- **WHEN** one task fails while more tasks remain pending than available jobs
- **THEN** no pending task starts after the terminal event and each receives
  exactly one cancelled result
- **AND** running tasks finish cleanup and the overall summary fails.

#### Scenario: Real broker faults remain bounded
- **WHEN** connected tasks exceed output, timeout, emit malformed protocol or
  leave descendants
- **THEN** public v5 returns bounded failure and cleanup completes as its
  contract requires
- **AND** scheduler neither manufactures pass nor leaves an owned survivor.

### Requirement: Scheduler v1 MUST remain dormant and authority-free
Scheduler v1 MUST NOT own Git selection, semantic inventory, release profiles,
runner/CI activation, receipts, review/publish or authority. No production
entrypoint MUST import or invoke it before exact later affected-profile
implementation.

Delivery MUST retain focused connected proof, production LOC at most 499,
exact authorization provenance and no history/full/live evidence. It receives
one fresh Sol/high review and one same-card repair opportunity.

#### Scenario: Dormancy scan rejects early activation
- **WHEN** focused proof scans tracked production entrypoints, scripts and CI
- **THEN** scheduler and scheduler-use of broker appear only in its dormant
  module and focused tests
- **AND** any baseline, CI, receipt or review/publish activation fails delivery.
