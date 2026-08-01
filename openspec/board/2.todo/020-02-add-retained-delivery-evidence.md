# Добавить retained delivery evidence

## Status
2.todo

## Owner
ChangeRail core

## OpenSpec Stage
story

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
- `add-retained-delivery-evidence` (planned)

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
- `openspec/changes/add-retained-delivery-evidence/`

## Verify
- Focused evidence capture/redaction smoke.
- Contract schema smoke.
- Review verdict and manifest validation smoke.
- Release baseline и public-surface scan.

## Related
- `openspec/board/1.backlog/020-00-one-command-delivery-experience-epic.md`
- `schemas/changerail-evidence-index.schema.json`
- `schemas/changerail-delivery-manifest.schema.json`
- `schemas/changerail-review-verdict.schema.json`

## Result
deliver-ready after series `010` exit audit

## Next
- `$chrl-deliver openspec/board/2.todo/020-02-add-retained-delivery-evidence.md`

## Log
- 2026-08-01T15:07:29Z requirement выделен из старого consumer postmortem.
- 2026-08-01T21:24:05Z readiness pass после серии `010`: карточка переведена
  в `2.todo`, добавлен ordered Change 1 для package runner.
