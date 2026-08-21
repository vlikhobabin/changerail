## Why

Runner уже умеет безопасно продолжать exact retained payload после
`investigation_required`, но корректная остановка на временно недоступной
внешней обязательной проверке не имеет machine-checkable resume path. Из-за
этого полезный payload сохраняется, однако оператор вынужден запускать
непротоколированное ручное продолжение.

## What Changes

- Ввести bounded taxonomy recoverable external blockers и value-free evidence
  contract с явным resume condition.
- Записывать retained identity и blocker metadata без заявления об успешной
  delivery и без ослабления review gate.
- Разрешить single-card resume только после свежей проверки prior status,
  blocker class, exact payload fingerprint и declared recovery evidence.
- Для проекта с declared execution target сохранять и повторно проверять exact
  target id/fingerprint; recovery не дает authority на provision, rebind или
  substitution.
- Расширить `resume-plan`, чтобы исходный child продолжался перед зависимой
  очередью, а уже доставленные карточки оставались skipped.
- Сохранить отдельный существующий authorization path для
  `investigation_required` и fail closed для неизвестных blocker classes.
- Требовать новый clean delivery attempt после явного target rebind вместо
  dirty retained resume.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-delivery-runner`: single-card и queue resume поддерживают
  проверяемое восстановление после временного внешнего blocker.
- `changerail-contracts`: delivery-run и plan-status schemas описывают blocker,
  resume evidence и retained recovery lineage.

## Impact

- `bin/changerail-delivery-runner`
- `schemas/changerail-delivery-run.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `scripts/smoke-delivery-runner.py`
- operator guidance для resume и external evidence
