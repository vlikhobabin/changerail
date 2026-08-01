# Добавить retained delivery evidence

## Status
1.backlog

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
- none yet

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
not started

## Next
- После `020-01` выполнить `$changerail-ff` для этой карточки.

## Log
- 2026-08-01T15:07:29Z requirement выделен из старого consumer postmortem.
