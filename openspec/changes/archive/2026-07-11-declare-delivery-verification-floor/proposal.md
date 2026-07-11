## Why

OPSX delivery должен выполнять обязательные проверки, объявленные проектом и
OpenSpec artifacts, но generic core не должен навязывать всем consumer projects
одинаковый formatter, type checker или environment matrix. Нужен явный
verification floor и evidence contract.

## What Changes

- Уточнить, что `opsx-do` обязан собрать verification floor из `AGENTS.md`,
  `openspec/config.yaml`, OpenSpec tasks/design и затронутого toolchain.
- Зафиксировать, что необъявленные formatter/type/environment checks не
  становятся mandatory только из-за generic OPSX workflow.
- Требовать записанный outcome для каждой обязательной команды и явное
  объяснение, когда RED evidence неприменима.
- Добавить проверку adequacy для измененных тестов: тест должен наблюдать
  заявленный источник поведения и быть способен упасть при регрессе.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `opsx-agent-methodology`: уточнить project-declared verification floor,
  evidence claims и test adequacy.
- `opsx-skill-surface`: уточнить delivery/review skill expectations для
  mandatory checks и evidence handoff.

## Impact

- `AGENTS.shared.md`
- `skills/opsx-do/SKILL.md`
- `skills/opsx-review/SKILL.md`
- `docs/how-it-works.md`
- OpenSpec specs/tasks for delivery verification behavior
