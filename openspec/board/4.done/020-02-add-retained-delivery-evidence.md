# Добавить retained delivery evidence

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
`020-one-command-delivery-experience`

## Series Index
`02`

## Source
- Consumer review мог проверить prose claims, но command outputs оставались
  transient и не имели общего capture contract.

## Summary
Добавить безопасный helper/contract для запуска verification commands с
retained ignored evidence и ссылками из manifest/verdict без помещения raw
logs в tracked payload.

## Acceptance
- Evidence helper сохраняет command identity, exit code, timestamps, concise
  observed summary и raw output path.
- Evidence files и index живут только под ignored runtime root.
- Secret-like arguments/output редактируются или capture останавливается с
  diagnostic.
- Manifest и verdict могут ссылаться на evidence IDs/paths.
- Helper различает mandatory, diagnostic и not-applicable evidence.
- Smokes покрывают success, failure, timeout, redaction и missing evidence.

## Scope
- Evidence index schema/helper и delivery/review integration.
- Verification command capture для ChangeRail-owned checks.

## Non-Goals
- Универсальный shell recorder для произвольных секретных команд.
- Коммит raw logs или screenshots.

## Depends On
- `020-01-formalize-deliver-ready-card-contract`
- `010-04-add-manifest-scope-and-handoff`

## Implementation Notes
- Использовать argv arrays, stable evidence IDs и atomic writes.
- Tracked card хранит только summary и ссылку на ignored evidence при
  необходимости.

## Change Set
- `add-retained-delivery-evidence` (archived:
  `openspec/changes/archive/2026-08-01-add-retained-delivery-evidence/`)

## Change 1: `add-retained-delivery-evidence`

### Why
Review and publish gates can validate summaries, but verification command
outputs are currently transient and lack a shared retained evidence contract.

### Goal
Add an ignored retained evidence mechanism that records safe command evidence
and allows manifests/verdicts to reference concise evidence without committing
raw logs.

### Scope
- Evidence index schema/helper and delivery/review integration.
- Verification command capture for ChangeRail-owned checks.

### Acceptance
- Evidence helper сохраняет command identity, exit code, timestamps, concise
  observed summary и raw output path.
- Evidence files и index живут только под ignored runtime root.
- Secret-like arguments/output редактируются или capture останавливается с
  diagnostic.
- Manifest и verdict могут ссылаться на evidence IDs/paths.
- Helper различает mandatory, diagnostic и not-applicable evidence.
- Smokes покрывают success, failure, timeout, redaction и missing evidence.

### Depends On
- `formalize-deliver-ready-card-contract`
- `add-manifest-scope-and-handoff`

### Related
- `openspec/changes/archive/2026-08-01-add-retained-delivery-evidence/`

## Verify
- `python3 scripts/smoke-retained-evidence.py` -> passed.
- `python3 scripts/smoke-contract-schemas.py` -> passed.
- `python3 scripts/smoke-delivery-manifest.py` -> passed.
- `python3 scripts/smoke-review-verdict-validation.py` -> passed.
- `ruff check bin scripts` -> passed.
- `python3 scripts/public-surface-scan.py` -> passed, 0 findings.
- `openspec validate add-retained-delivery-evidence --strict` -> passed before
  archive.
- `openspec validate --all --strict` -> passed after archive, 14 specs.
- `git diff --check` -> passed.
- `python3 scripts/run-release-baseline.py` -> passed under retained evidence
  `release-baseline` at
  `.runtime/changerail/evidence/020-02-add-retained-delivery-evidence/index.json`.

## Archive
- `openspec/changes/archive/2026-08-01-add-retained-delivery-evidence/`

## Related
- `openspec/board/1.backlog/020-00-one-command-delivery-experience-epic.md`
- `schemas/changerail-evidence-index.schema.json`
- `schemas/changerail-delivery-manifest.schema.json`
- `schemas/changerail-review-verdict.schema.json`

## Result
Implementation, spec sync and archive complete; fresh independent review
pending before publish.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-08-01T15:07:29Z requirement выделен из старого consumer postmortem.
- 2026-08-01T21:24:05Z readiness pass после серии `010`: карточка переведена
  в `2.todo`, добавлен ordered Change 1 для package runner.
- 2026-08-01T22:00:53Z ff: созданы apply-ready artifacts для
  `add-retained-delivery-evidence`, карточка переведена в `3.inprogress`.
- 2026-08-01T22:20:45Z do: реализован retained evidence helper/contract,
  specs синхронизированы, change archived, release baseline passed with
  retained evidence `release-baseline`.
- 2026-08-01T22:32:08Z review cycle 1 returned `no-go` for runtime-only
  `--index` enforcement and standalone `not_applicable` notes; scoped fixes
  added with retained-evidence regression smoke coverage.
- 2026-08-01T22:42:15Z review cycle 2 returned `no-go` for partial
  authorization-style output redaction; scoped fix now redacts full
  secret-like output line values with regression smoke coverage.
- 2026-08-01T22:56:24Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
