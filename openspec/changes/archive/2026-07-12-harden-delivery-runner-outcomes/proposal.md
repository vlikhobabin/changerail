## Why

Non-interactive delivery runner является supervisor boundary. Его terminal
outcome должен приходить из documented structured events или process exit, а не
из arbitrary strings внутри JSON fields; release checks должны покрывать каждую
public contract schema.

## What Changes

- Ограничить runner terminal outcome parsing документированными event types и
  terminal fields.
- Сохранить lifecycle ordering, чтобы later authoritative terminal events могли
  supersede earlier non-terminal errors, а conflicting terminal events
  разрешались deterministic.
- Добавить runner smoke coverage для ordered events, successful exit после
  non-terminal tool errors, non-zero exit без outcome, authoritative no-go и
  awaiting-review.
- Расширить `verify-project` и related smoke/release docs, чтобы покрыть все
  пять public contract schemas: review verdict, review cycle history, delivery
  manifest, delivery run и evidence index.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-delivery-runner`: terminal outcome parsing ужесточен до
  documented structured events и fields.
- `changerail-project-verification`: schema coverage расширен до всех public
  ChangeRail contract schemas.
- `changerail-contracts`: docs/specs уточняют complete schema set, покрытый
  release и verification gates.

## Impact

- `bin/changerail-delivery-runner`
- `bin/verify-project`
- `scripts/smoke-delivery-runner.py`
- `scripts/smoke-verify-project.py`
- `docs/changerail-contracts.md`
- `docs/release-discipline.md`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `openspec/specs/changerail-project-verification/spec.md`
- `openspec/specs/changerail-contracts/spec.md`
