## Context

ChangeRail can run in its own repository and orchestrate consumer repositories.
In a queue plan, there are three distinct layers: aggregate plan runner,
single-card delivery runner and Codex launcher. The docs need to separate these
layers so consumers can set up auth and command paths without committing local
launcher wrappers.

## Decisions

- Describe the launcher chain in user-facing docs as:
  `run-plan/preflight-plan` -> single-card `run/preflight` -> `codex exec`.
- State that the tracked ChangeRail runner is the command being invoked by the
  operator, while each child receives workspace-specific environment.
- Document `CODEX_WORKDIR=<workspace>` and default effective
  `CODEX_HOME=<workspace>/.codex`, unless the operator explicitly sets
  `CODEX_HOME`.
- Avoid telling consumers to add tracked `bin/codex`; mention repo-local
  launcher only as an optional convenience if they already maintain one.

## Public Safety

Examples must use `/opt/example-project`, `/opt/example-workspace` and
non-secret auth marker descriptions only. Docs must not include real local
workspace names, credential paths or tokens.
