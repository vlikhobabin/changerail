## Context

`bin/changerail-delivery-runner` writes one
`changerail.delivery-run.v1` record per single-card run under
`.runtime/changerail/delivery-runs/<run-id>/status.json`. Queue-level
inspection already exists through `status-plan`, but a single-card operator
still has to know runtime paths and inspect multiple ignored JSON files to
answer whether the card is running, blocked, waiting for review, or ready for a
specific manual continuation.

The source of truth must remain existing ignored runtime records. This change
adds a read-only view over those records; it does not introduce a new daemon,
writer, scheduler, mutable state transition or browser UI.

## Goals / Non-Goals

**Goals:**
- Add `bin/changerail-delivery-runner status` as the single-card counterpart to
  existing `status-plan`.
- Support status selection by explicit `status.json` path, by `--run-id`, or by
  latest record under the effective workspace runtime root.
- Validate selected `changerail.delivery-run.v1` input before displaying it.
- Show compact human-readable attention fields from status and canonical
  related runtime artifacts when they are unambiguous.
- Reuse existing schemas for delivery-run, delivery-manifest, review verdict
  and evidence records.
- Keep `--json` schema-stable by returning the selected source
  `changerail.delivery-run.v1` record.

**Non-Goals:**
- Add a unified reader for both plan status and single-card status in this
  change; `status-plan` remains the aggregate queue reader.
- Add or modify public schema ids.
- Infer next action from raw stdout/stderr, session prose or process tree
  state.
- Start, stop, resume or recover delivery processes.
- Rewrite runtime manifests, verdicts, evidence indexes or status files.

## Decisions

### Command shape

Add a top-level `status` subcommand:

```bash
bin/changerail-delivery-runner status [status.json] [--workspace <path>] [--runtime-root <path>] [--run-id <id>] [--json]
```

Selection precedence is explicit path, then `--run-id`, then latest status in
the effective runtime root. If multiple inputs are supplied, the command should
fail closed rather than choose silently. Latest selection is only a convenience
inside one runtime root; it is not a cross-workspace discovery mechanism.

Alternative considered: extend `status-plan` to also read single-card records.
Rejected for this change because `status-plan` already means aggregate
`changerail.delivery-plan-status.v1`, while the card acceptance explicitly says
triage should decide whether a future common reader is needed.

### Validation and exit behavior

The selected status record must validate against
`schemas/changerail-delivery-run.schema.json`. Missing files, JSON parse errors,
schema errors and unsupported schema ids return non-zero with a concise
diagnostic. Explicit corrupt input must not fall back to another record.

Related manifest, review verdict and evidence paths are derived only from the
validated status card id/path and the effective workspace. When a canonical
related artifact exists, the command validates it before using its structured
fields. If validation fails, human output marks the related artifact invalid and
the command exits non-zero; it does not scrape raw logs or guess alternate
paths.

### Human output

Human output prints stable key-value lines optimized for operator scanning:

- `card`
- `phase`
- `result`
- `updated_at`
- `terminal_reason` when present
- `status`
- `manifest`
- `review_verdict`
- `review_history` when present
- `evidence`

When a valid manifest includes `runtime_pause_reasons`, the command prints each
reason's existing `summary` and `next_action`. These values come only from the
manifest contract. The command does not synthesize advice from child logs,
terminal prose, stale process state or missing PID checks.

### JSON output

`--json` emits the selected `changerail.delivery-run.v1` source record after
validation, preserving existing machine-readable contracts. A separate minimal
attention-view schema is intentionally deferred because the first use case is a
human convenience view and the source record already has a stable schema for
automation. A future change can add a schema-backed view if another machine
consumer needs linked manifest/verdict/evidence summaries in one JSON object.

### Documentation and smoke coverage

`docs/changerail-contracts.md` and `docs/how-it-works.md` should list the new
single-card status command next to `run`, `resume` and `status-plan`, including
the distinction between single-card status and aggregate plan status.

`scripts/smoke-delivery-runner.py` should add synthetic runtime fixtures that
cover:

- explicit status path success;
- `--run-id` or latest selection;
- blocked/no-go terminal diagnostics;
- valid manifest pause reason rendering;
- corrupt or unsupported input failure;
- read-only behavior, demonstrated by stable mtime or content comparison of the
  selected status and linked runtime artifacts.

## Risks / Trade-offs

- **Latest selection can hide ambiguity** -> keep the search scoped to one
  runtime root and document explicit path or `--run-id` as the deterministic
  operator path.
- **Linked artifact validation can make a convenience command fail** -> fail
  closed is preferable because invalid runtime evidence should not be displayed
  as trustworthy attention guidance.
- **Human output is not a machine contract** -> `--json` returns the source
  record until a separate schema-backed view has a proven consumer.
