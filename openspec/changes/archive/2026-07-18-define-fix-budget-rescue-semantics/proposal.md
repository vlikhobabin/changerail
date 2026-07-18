## Why

Pre-review `changerail-do` fix budget и post-review `NO-GO` rescue budget сейчас
имеют независимые stop rules. Из-за этого исчерпание `--max-fix-cycles` может
превратиться в ручной запрос увеличить budget, хотя autonomous
`changerail-deliver` должен либо выполнить bounded локальный rescue, либо
перенести отдельную работу в linked recovery card.

## What Changes

- Ввести единый transition contract из `fix_budget_exhausted` в
  `changerail-deliver` без смешивания fix cycles и review cycles.
- Разделить три ветви: bounded same-card micro-fix, linked
  rescue/replacement для отдельного scope и external `BLOCKED`/
  `NOT-VERIFIABLE`.
- Запретить exceptional manual budget как default continuation path.
- Синхронизировать shared methodology, lifecycle skills, public docs и
  consumer template guidance.
- Зафиксировать machine-readable non-delivered reason для fix-budget safety
  stop, который runner enforcement реализует следующим change.

## Capabilities

### New Capabilities

- none.

### Modified Capabilities

- `changerail-agent-methodology`: добавить общий fix-budget escalation contract
  и правила выбора same-card, linked-card и external-blocker ветвей.
- `changerail-skill-surface`: согласовать `changerail-do` и
  `changerail-deliver`, включая structured handoff и отсутствие manual override
  по умолчанию.
- `changerail-project-templates`: передавать различие fix/review budgets и
  autonomous recovery guidance новым consumer projects.

## Impact

Затрагиваются `AGENTS.shared.md`, canonical lifecycle skills, связанные Claude
wrappers только при необходимости, methodology docs, bootstrap templates и
smoke checks их generated guidance. Wire schema не меняется в этом change;
runner enforcement выполняется зависимым change.
