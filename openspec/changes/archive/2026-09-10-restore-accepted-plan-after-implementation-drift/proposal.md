## Why

После случайной правки замороженного `Next` stopped native run оказывается между
проверкой принятого плана и проверкой точного payload. Возврат исходного текста
исправляет первую идентичность и нарушает вторую; общего штатного перехода с
сохранением checkpoint, evidence и истории сейчас нет.

## What Changes

- Добавить явную подготовку и применение восстановления только исходных байтов
  `Next`, с проверкой accepted contract и остального payload до любых изменений.
- Записывать отдельную неизменяемую квитанцию и effective manifest; сохранять
  исходный run и все неудачные продолжения без дополнений и перезаписи.
- Продолжать через штатный runner с сохранёнными task groups и review allowance,
  обновляя доказательства, потерявшие актуальность.
- Описать ограниченный переход установленного predecessor на новую execution
  identity через проверенные runtime archives; обновление само по себе не
  разрешает recovery. Исторические read-only runs остаются недоступными.
- Уточнить диагностику drift и разрешённые правки карточки в native skill;
  документировать подготовку, apply, прерывание и точное продолжение.

## Capabilities

### New Capabilities

Нет отдельных новых capabilities.

### Modified Capabilities

- `native-delivery`: явное восстановление accepted plan, append-only lineage,
  актуализация evidence и ограниченная совместимость установленного predecessor.

## Impact

Изменяются native recovery/admission/execution boundaries, новый модуль и схема
restoration receipt, CLI и consumer installation transition при необходимости,
регрессии recovery/evidence/accounting и операторская документация.
Изменения инструмента принадлежат ChangeRail. Код, данные и запуски конкретного
потребителя не входят в реализацию. Live 1С и внешняя публикация не требуются.
Обычные resume и runtime-repair сохраняют прежние ограничения.
