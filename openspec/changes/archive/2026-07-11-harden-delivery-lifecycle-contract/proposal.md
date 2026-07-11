## Why

Длительный OPSX delivery сейчас может завершать OpenSpec changes, но
недостаточно жестко разделяет завершение change, независимый review, publish и
финализацию story на доске. Это создает риск преждевременного `4.done` и
неполного publish scope при перемещениях карточки.

## What Changes

- Уточнить lifecycle story/card: `opsx-do` архивирует card-owned changes, но
  оставляет карточку в `3.inprogress` до review/publish.
- Зафиксировать, что independent review проверяет полный delivery payload, а
  содержательные изменения после `go` инвалидируют verdict.
- Расширить delivery manifest contract так, чтобы publish scope мог выражать
  `add`, `modify`, `delete` и `rename` операции, включая оба пути при
  перемещении board card.
- Обновить lifecycle skills и docs, чтобы board finalization в `4.done` была
  детерминированным post-publish шагом.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `opsx-agent-methodology`: уточнить story lifecycle, archive-before-review и
  done-after-publish contract.
- `opsx-contracts`: расширить delivery manifest contract для file operations и
  staging proposal completeness.
- `opsx-skill-surface`: уточнить обязанности `opsx-do`, `opsx-review`,
  `opsx-pub` и `opsx-deliver` вокруг review-gated lifecycle.

## Impact

- `AGENTS.shared.md`
- `docs/how-it-works.md`
- `docs/opsx-contracts.md`
- `skills/opsx-do/SKILL.md`
- `skills/opsx-pub/SKILL.md`
- `skills/opsx-deliver/SKILL.md`
- `skills/opsx-do/references/opsx-delivery-manifest.md`
- `schemas/opsx-delivery-manifest.schema.json`
- manifest helper/smoke tests for move/delete staging scope
