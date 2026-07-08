## Context

The repository already has local red/green scripts for wiring discovery,
bootstrap, verify-project and drift. The missing release-discipline piece is a
CI workflow that composes those checks and can be inspected locally.

## Decisions

- Add `.github/workflows/opsx-ci.yml` with triggers for `push`,
  `pull_request` and `workflow_dispatch`.
- Use the repo-local `./bin/openspec` wrapper in CI so OpenSpec CLI resolution
  follows OPSX compatibility policy.
- Run:
  - `./bin/openspec validate --all --strict`
  - JSON/TOML config parsing baseline from `AGENTS.md`
  - `python3 -m py_compile` for executable Python scripts
  - `python3 scripts/smoke-release-ci.py`
  - `python3 scripts/smoke-wiring-discovery.py`
  - `python3 scripts/smoke-verify-project.py`
  - `python3 scripts/smoke-bootstrap-project.py`
  - `bin/bootstrap-project` into `.runtime/opsx/ci-drift/example-project`
  - `python3 scripts/smoke-drift.py --project <generated-project>`
- Keep CI-generated projects and reports under ignored `.runtime/`.
- Implement `scripts/smoke-release-ci.py` as a small fail-closed contract check
  for workflow presence and required command strings. This avoids adding a
  runtime dependency on a YAML parser.

## Non-Goals

- Не публиковать release artifacts.
- Не подключать private workspace inventory к CI.
- Не добавлять dependency manager или package lock.

## Public Safety

CI must use generated generic fixtures only. It must not reference local
private project names, real workspace roots or operator-specific inventory.
