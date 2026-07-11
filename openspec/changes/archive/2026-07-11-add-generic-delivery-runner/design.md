## Context

`bin/codex` sets `CODEX_HOME` and `CODEX_WORKDIR`, but supervised operations
need a tracked wrapper for repeatable non-interactive delivery runs. The runner
must avoid private workspace assumptions, support per-run overrides through
documented Codex CLI options and write machine-readable status that a
supervisor can poll.

## Goals / Non-Goals

**Goals:**
- Provide a generic non-interactive runner for one OPSX card.
- Close child stdin to avoid background `codex exec` waiting on inherited
  terminal input.
- Support per-run model and reasoning effort without changing repo defaults.
- Write atomic JSON status/run records with terminal outcomes.
- Provide a preflight path for binary, `CODEX_HOME`, auth/config and optional
  connectivity checks.

**Non-Goals:**
- Do not replace the interactive `$opsx-deliver` skill.
- Do not run review in the same context as implementation.
- Do not write runtime records to tracked source.

## Decisions

- Implement the runner as a Python executable under `bin/`.
  - Rationale: it can atomically write JSON, normalize paths and avoid shell
    quoting hazards while remaining dependency-free.
  - Alternative considered: bash wrapper. JSON/status handling would be more
    fragile.
- Invoke `codex exec` through `bin/codex` by default.
  - Rationale: preserves the repo-scoped launcher and existing `CODEX_HOME`
    behavior.
  - Alternative considered: call `codex` directly. That bypasses documented
    OPSX setup.
- Use `-m <model>` and `-c model_reasoning_effort="<effort>"` for overrides.
  - Rationale: these are documented by the installed Codex CLI's model and
    config override surfaces.
- Parse Codex JSONL opportunistically for usage.
  - Rationale: the CLI event stream may evolve; absent usage should be recorded
    as unknown instead of guessed.

## Risks / Trade-offs

- Codex event schemas may change -> runner stores raw stdout/stderr in ignored
  runtime state and treats usage as optional.
- Connectivity checks can be environment-specific -> the runner supports an
  explicit URL and the runbook explains that projects choose the endpoint.
