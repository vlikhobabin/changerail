# Добавить consumer profiles и severity в verify-project

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
`010-core-release-contracts`

## Series Index
`05`

## Source
- Codex-first consumer намеренно не использовал часть legacy surfaces и имел
  известный project-wide OpenSpec debt.

## Summary
Сделать `verify-project` profile-aware и severity-aware, сохранив fail-closed
default: project policy может объявить surface required/optional/forbidden и
отдельно классифицировать baseline diagnostics, но не скрывать blocking failure.

## Acceptance
- Project profile объявляет Codex, Claude и legacy MCP surfaces как required,
  optional или forbidden.
- Checks имеют stable status/severity contract и machine-readable summary.
- Только non-blocking findings могут давать `pass-with-diagnostics`.
- Targeted card-owned OpenSpec validation остается обязательной.
- Project-wide baseline debt допускается как diagnostic только при явной
  tracked policy с видимым residual risk.
- Default profile сохраняет текущий строгий all-surfaces behavior.
- Positive/negative smokes покрывают Codex-only, all-surfaces, forbidden
  artifact и попытку ослабить mandatory check.

## Scope
- `bin/verify-project`, JSON output contract и project config/template docs.
- Verification specs и deterministic fixtures.

## Non-Goals
- Автоматическое исправление legacy OpenSpec debt.
- Native Windows path/link semantics: серии `030` и `040`.

## Depends On
- `010-02-establish-supported-python-runtime`
- `010-04-add-manifest-scope-and-handoff`

## Implementation Notes
- Разделить `status` и `severity`; `skip` не должен маскировать required check.
- Forbidden surface должен падать, если artifact присутствует.
- Не смешивать delivery auth advisory с structural verification outcome.

## Change Set
- `add-verification-profiles-and-severity` (archived:
  `openspec/changes/archive/2026-08-01-add-verification-profiles-and-severity/`)

## Change 1: `add-verification-profiles-and-severity`

### Why
`verify-project` сейчас не различает required/optional/forbidden consumer
surfaces и blocking/non-blocking diagnostics, из-за чего Codex-only projects и
project-wide baseline debt требуют ручной интерпретации.

### Goal
Добавить profile-aware и severity-aware verification contract с fail-closed
default и явным `pass-with-diagnostics` только для non-blocking findings.

### Scope
- `bin/verify-project`, JSON output contract и project config/template docs.
- Verification specs и deterministic fixtures.
- Generated project bootstrap/verify smoke matrix.

### Acceptance
- Project profile объявляет Codex, Claude и legacy MCP surfaces как required,
  optional или forbidden.
- Checks имеют stable status/severity contract и machine-readable summary.
- Только non-blocking findings могут давать `pass-with-diagnostics`.
- Targeted card-owned OpenSpec validation остается обязательной.
- Project-wide baseline debt допускается как diagnostic только при явной
  tracked policy с видимым residual risk.
- Default profile сохраняет текущий строгий all-surfaces behavior.
- Positive/negative smokes покрывают Codex-only, all-surfaces, forbidden
  artifact и попытку ослабить mandatory check.

### Depends On
- `establish-supported-python-runtime`
- `add-manifest-scope-and-handoff`

### Related
- `openspec/changes/archive/2026-08-01-add-verification-profiles-and-severity/`

## Verify
- `./bin/openspec validate add-verification-profiles-and-severity --strict` passed.
- `./bin/openspec validate --all --strict` passed.
- `git diff --check` passed.
- `python3 scripts/smoke-verify-project.py` passed
  (`summary: pass (24/24 passed, 0 failed)`).
- `python3 scripts/smoke-bootstrap-project.py` passed
  (`summary: pass (8/8 passed, 0 failed)`).
- `python3 scripts/public-surface-scan.py` passed
  (`summary: pass (610 files scanned, 0 findings)`).
- `python3 scripts/public-surface-scan.py --history` passed
  (`summary: pass (610 files scanned, 0 findings)`).
- `python3 scripts/run-release-baseline.py` passed (`{"status": "pass",
  "steps": 26}`).

## Archive
- `openspec/changes/archive/2026-08-01-add-verification-profiles-and-severity/`

## Related
- `openspec/board/1.backlog/010-00-core-release-contracts-epic.md`
- `bin/verify-project`
- `openspec/specs/changerail-project-verification/spec.md`
- `templates/project/openspec/config.yaml.tpl`

## Result
implemented, verified, synced, archived and finalized through ChangeRail scoped
publish after review cycle 2 `go`; review cycle 1 `no-go` blocker fixed in
scope. Exact payload and published commit ledger is retained in the ignored
delivery manifest.

## Next
- done

## Log
- 2026-08-01T15:07:29Z requirements нормализованы из consumer feedback.
- 2026-08-01T15:45:00Z карточка переведена в `2.todo` для runner delivery.
- 2026-08-01T20:29:41Z OpenSpec artifacts созданы и проверены:
  `./bin/openspec validate add-verification-profiles-and-severity --strict`,
  `./bin/openspec validate --all --strict`, `git diff --check`; карточка
  переведена в `3.inprogress`.
- 2026-08-01T20:47:06Z implementation завершена: verifier стал
  profile/severity-aware, templates/docs обновлены, specs synced, change
  archived as
  `openspec/changes/archive/2026-08-01-add-verification-profiles-and-severity/`;
  release baseline и public-surface scans passed.
- 2026-08-01T20:54:14Z independent review cycle 1 returned `no-go`: R1 found
  that tracked `baseline_debt` could downgrade a card-owned active OpenSpec
  validation failure to `pass-with-diagnostics`.
- 2026-08-01T21:02:43Z R1 fixed in card scope: `verify-project` now validates
  active OpenSpec changes through a separate blocking `targeted OpenSpec
  validation` check before project-wide baseline debt downgrade; focused smoke
  covers the false-green case and passes 24/24; release baseline passes 26/26.
- 2026-08-01T21:08:54Z independent review cycle 2 returned `go` with 0
  blocker, 0 major and 0 minor findings.
- 2026-08-01T21:16:16Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
