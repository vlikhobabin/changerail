# Bootstrap и templates (Фаза 2)

## Status
4.done

## Owner
Codex

## OpenSpec Stage
archived

## Source
- OPSX roadmap, раздел 12, Фаза 2 (`docs/opsx-source-of-truth-architecture.md`).
- Разделы 10 (Bootstrap) и 11 (Verification и drift).

## Summary
Дать возможность создавать новый проект-потребитель одной командой: собрать
`templates/project`, реализовать `bin/bootstrap-project` и красно-зеленый gate
`bin/verify-project`, проверить всё на smoke-проекте в ignored `.runtime`.

## Acceptance
- `templates/project/` содержит `AGENTS.md.tpl`, `CLAUDE.md.tpl`, `gitignore.tpl`,
  `mcp.json.tpl`, `codex-config.toml.tpl` и `openspec/` заготовку.
- Placeholders для project path, project name и project kind задокументированы.
- `bin/verify-project <path>` — красно-зеленый gate (exit-код), проверяет
  symlink-и, разрешаемость в OPSX (прямо или через aggregator), `openspec/config.yaml`,
  `openspec validate --all`, MCP/Codex scope, достижимость контрактов/schemas и
  игнор runtime/auth путей.
- `bin/bootstrap-project` создает каталоги, symlink-и и generated файлы,
  refuse-on-existing по умолчанию, поддерживает dry-run/backup и запускает
  `verify-project`.
- Smoke-проект под `.runtime` проверяет bootstrap end-to-end и не коммитится.
- Public examples остаются generic (`/opt/example-project`).

## Change Set
- `add-project-bootstrap-templates`
- `add-project-verify-gate`
- `add-project-bootstrap-command`

## Verify
- passed: `openspec validate add-project-bootstrap-templates --strict`
- passed: `openspec validate add-project-verify-gate --strict`
- passed: `openspec validate add-project-bootstrap-command --strict`
- passed: `openspec validate opsx-project-templates --strict`
- passed: `openspec validate opsx-project-verification --strict`
- passed: `openspec validate opsx-project-bootstrap --strict`
- passed: `openspec validate --all --strict`
- passed: `python3 -m py_compile bin/bootstrap-project bin/verify-project
  scripts/smoke-bootstrap-project.py scripts/smoke-verify-project.py`
- passed: `python3 scripts/smoke-verify-project.py` -> 2/2 checks, report
  `.runtime/opsx/verify-project-smoke/20260708T155221Z-2c08d049/report.json`
- passed: `python3 scripts/smoke-bootstrap-project.py` -> 4/4 checks, report
  `.runtime/opsx/bootstrap-smoke/20260708T155630Z-68018bcb/report.json`
- passed: `python3 -m json.tool .mcp.json`
- passed: `python3 -m json.tool
  .runtime/opsx/delivery-manifests/02-bootstrap-and-templates.json`
- passed: `.codex/config.toml` parsed with Python `tomllib`
- passed: targeted public-surface scan for private/machine-local paths
- passed: `git diff --check`
- passed: text whitespace scan over modified and untracked files
- passed: `python3 scripts/opsx_review_verdict.py validate
  .runtime/opsx/reviews/02-bootstrap-and-templates.json --check-fresh
  --workspace . --json` returned fresh external `go`

## Archive
- `openspec/changes/archive/2026-07-08-add-project-bootstrap-templates/`
- `openspec/changes/archive/2026-07-08-add-project-verify-gate/`
- `openspec/changes/archive/2026-07-08-add-project-bootstrap-command/`

## Related
- `docs/opsx-source-of-truth-architecture.md`
- `docs/wiring-discovery.md`
- `scripts/smoke-wiring-discovery.py`
- `openspec/changes/archive/2026-07-08-add-project-bootstrap-templates/`
- `openspec/changes/archive/2026-07-08-add-project-verify-gate/`
- `openspec/changes/archive/2026-07-08-add-project-bootstrap-command/`
- `openspec/specs/opsx-project-templates/spec.md`
- `openspec/specs/opsx-project-verification/spec.md`
- `openspec/specs/opsx-project-bootstrap/spec.md`
- `templates/project/`
- `bin/verify-project`
- `bin/bootstrap-project`
- `scripts/smoke-verify-project.py`
- `scripts/smoke-bootstrap-project.py`

## Result
Implemented and archived all planned Phase 2 bootstrap/template changes.
External review returned a fresh `go` verdict; publish proceeds with ignored
runtime artifacts excluded.

## Next
- Continue with `openspec/board/1.backlog/03-drift-gate.md`.

## Change 1: `add-project-bootstrap-templates`

### Why
Новые проекты-потребители должны получать одинаковый public-safe skeleton без
ручного копирования OPSX wiring и OpenSpec board.

### Goal
Добавить `templates/project/` с обязательными шаблонами и documented
placeholders для project path, project name и project kind.

### Scope
- `templates/project/AGENTS.md.tpl`
- `templates/project/CLAUDE.md.tpl`
- `templates/project/gitignore.tpl`
- `templates/project/mcp.json.tpl`
- `templates/project/codex-config.toml.tpl`
- `templates/project/openspec/` skeleton
- README/runbook для placeholders и generated-file choices.

### Acceptance
- Шаблоны содержат только generic examples (`/opt/opsx`,
  `/opt/example-project`) и documented placeholders.
- OpenSpec skeleton содержит `openspec/config.yaml`, board layout и пустые
  `changes/`/`specs/`.
- Template docs объясняют какие файлы генерируются, какие symlink-и создаются
  bootstrap command и какие runtime/auth paths должны игнорироваться.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-08-add-project-bootstrap-templates/`

## Change 2: `add-project-verify-gate`

### Why
Bootstrap без gate не дает сопровождающему deterministic red/green сигнал, что
проект действительно подключен к OPSX source of truth.

### Goal
Добавить `bin/verify-project <path>` как exit-code gate для consumer project
wiring, config, contracts, OpenSpec validation и ignored runtime/auth paths.

### Scope
- `bin/verify-project`
- focused helper logic under `scripts/` if needed
- docs/spec updates for verification behavior.

### Acceptance
- Gate fails for missing/broken required symlink-и, missing configs, invalid
  OpenSpec config, missing contract helpers/schemas or unignored runtime/auth
  paths.
- Gate accepts symlink-и resolving directly to `/opt/opsx` or through a
  documented aggregator path.
- Gate validates `.mcp.json`, `.codex/config.toml`, `openspec/config.yaml` and
  runs project-local `bin/openspec validate --all --strict`.

### Depends On
- `add-project-bootstrap-templates`

### Related
- `openspec/changes/archive/2026-07-08-add-project-verify-gate/`

## Change 3: `add-project-bootstrap-command`

### Why
Новый потребитель должен создаваться одной командой, а не последовательностью
ручных mkdir/symlink/template операций.

### Goal
Добавить `bin/bootstrap-project`, который создает consumer skeleton из
`templates/project`, подключает OPSX symlink-и, поддерживает dry-run/backup,
refuse-on-existing по умолчанию и запускает `verify-project`.

### Scope
- `bin/bootstrap-project`
- ignored smoke project under `.runtime` during verification
- `scripts/smoke-bootstrap-project.py`
- docs/README updates for current quickstart.

### Acceptance
- Bootstrap creates required directories, symlink-и and generated files for a
  new generic consumer project.
- Existing non-empty targets are refused unless backup mode is explicitly used.
- Dry-run prints planned actions without creating the project.
- Smoke verifies bootstrap end-to-end under `.runtime` and leaves no tracked
  runtime artifacts.

### Depends On
- `add-project-bootstrap-templates`
- `add-project-verify-gate`

### Related
- `openspec/changes/archive/2026-07-08-add-project-bootstrap-command/`

## Log
- 2026-07-08T14:05:27Z card created from roadmap phase 2 scope.
- 2026-07-08T16:00:00Z opsx-ff decomposed the card into three apply-ready
  changes and moved it to `2.todo`.
- 2026-07-08T16:10:00Z archived `add-project-bootstrap-templates` after
  syncing `opsx-project-templates` and validating OpenSpec plus whitespace.
- 2026-07-08T16:20:00Z archived `add-project-verify-gate` after
  `smoke-verify-project.py`, config parsing, OpenSpec validation and
  whitespace checks passed.
- 2026-07-08T16:30:00Z archived `add-project-bootstrap-command` after
  bootstrap smoke 4/4, OpenSpec validation, config parsing, public-surface
  scan and whitespace checks passed.
- 2026-07-08T16:31:00Z safety stop: awaiting external review per supervisor
  instruction; no self-review, reviewer launch, publish, commit or push was
  performed.
- 2026-07-08T16:59:20Z external review cycle 1 returned `go`; verdict
  validated fresh against HEAD `2e49c5752ba3cdece2f7cd589099426a67885156`
  with fingerprint
  `sha256:d58849406db2f35c0f9979cced111ee55e51a286ab4368e64b82e20b722973b7`.
- 2026-07-08T16:59:20Z card moved to `4.done` for scoped publish; runtime
  review verdict and delivery manifest remain excluded from commit.
