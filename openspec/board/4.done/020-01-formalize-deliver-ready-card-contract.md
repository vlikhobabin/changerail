# Формализовать deliver-ready contract карточки

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
`020-one-command-delivery-experience`

## Series Index
`01`

## Source
- Consumer operator feedback от 2026-08-01.

## Summary
Определить `deliver-ready` как проверяемое свойство принятой story, а не новую
board lane: карточка scoped, owned, имеет observable acceptance, ordered change
plan и известные gates, но OpenSpec artifacts еще могут отсутствовать.

## Acceptance
- `deliver-ready` определен в shared methodology, board docs и templates.
- Для стандартной доски состояние соответствует принятой карточке в `2.todo`
  с ordered plan; новая шестая колонка не добавляется.
- OpenSpec artifacts не являются precondition для запуска `$chrl-deliver`.
- `$chrl-deliver <card>` представлен как normal operator handoff.
- `ff/do/review/pub` описаны как internal phases или явные
  repair/debug/manual-resume commands.
- Templates позволяют подготовить deliver-ready card без premature changes.

## Scope
- Shared agent methodology, board docs/templates и deliver/ff wording.
- Readiness diagnostics в runner только если они остаются advisory до явного
  принятия карточки.

## Non-Goals
- Автоматическое product triage без operator authority.
- Создание OpenSpec artifacts при заполнении карточки.

## Depends On
- Серия `010-core-release-contracts` завершена.

## Implementation Notes
- Избегать второго независимого status field, который может расходиться с
  board path.
- Readiness predicate должен объяснять missing criteria, а не только отдавать
  boolean.

## Change Set
- `formalize-deliver-ready-card-contract`

## Change 1: `formalize-deliver-ready-card-contract`

### Why
Accepted board cards can currently be handed to phase commands or
`$chrl-deliver` with ambiguous readiness language, so operators still infer
whether OpenSpec artifacts are required before delivery.

### Goal
Define `deliver-ready` as the accepted-card contract for normal one-command
handoff while keeping `ff/do/review/pub` as internal phases or explicit repair
surfaces.

### Scope
- Shared methodology, board docs, templates and skill wording.
- Advisory readiness diagnostics if they stay non-blocking before card
  acceptance.

### Acceptance
- `deliver-ready` определен в shared methodology, board docs и templates.
- Для стандартной доски состояние соответствует принятой карточке в `2.todo`
  с ordered plan; новая шестая колонка не добавляется.
- OpenSpec artifacts не являются precondition для запуска `$chrl-deliver`.
- `$chrl-deliver <card>` представлен как normal operator handoff.
- `ff/do/review/pub` описаны как internal phases или явные
  repair/debug/manual-resume commands.
- Templates позволяют подготовить deliver-ready card без premature changes.

### Depends On
- `010-core-release-contracts`

### Related
- `openspec/changes/archive/2026-08-01-formalize-deliver-ready-card-contract/`

## Verify
- `openspec validate formalize-deliver-ready-card-contract --strict` passed.
- `openspec validate --all --strict` passed with 15 items.
- Docs/template consistency smoke for `deliver-ready`, `$chrl-deliver` and
  five board columns passed.
- `python3 scripts/smoke-bootstrap-project.py` passed: 8/8 checks.
- `python3 scripts/smoke-wiring-discovery.py` passed: 172/172 checks.
- `openspec validate changerail-agent-methodology --strict` passed.
- `openspec validate changerail-project-templates --strict` passed.
- `openspec validate changerail-skill-surface --strict` passed.
- `openspec validate --all --strict` passed after spec sync with 15 items.
- `bin/openspec archive formalize-deliver-ready-card-contract --yes --skip-specs`
  passed after manual spec sync.
- `git diff --check` plus trailing-whitespace scan for untracked files passed.
- `python3 scripts/public-surface-scan.py ...` passed for touched docs,
  templates, skills and OpenSpec artifacts: 15 files, 0 findings.
- `python3 scripts/run-release-baseline.py` passed: 26/26 steps, including
  public-surface scan and history scan with 618 files, 0 findings.

## Archive
- `openspec/changes/archive/2026-08-01-formalize-deliver-ready-card-contract/`

## Related
- `openspec/board/1.backlog/020-00-one-command-delivery-experience-epic.md`
- `AGENTS.shared.md`
- `docs/board-and-two-agent-feature-flow.md`
- `templates/project/openspec/board/README.md.tpl`

## Result
implemented, verified, synced, archived, reviewed and published

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-08-01T15:07:29Z исходная карточка уточнена без введения новой board lane.
- 2026-08-01T21:24:05Z readiness pass после серии `010`: карточка переведена
  в `2.todo`, добавлен ordered Change 1 для package runner.
- 2026-08-01T21:31:58Z `$chrl-deliver` fast-forward phase created apply-ready
  OpenSpec artifacts for `formalize-deliver-ready-card-contract` and moved the
  card to `3.inprogress`.
- 2026-08-01T21:39:22Z implemented deliver-ready docs/templates/skill wording,
  synced specs and archived
  `openspec/changes/archive/2026-08-01-formalize-deliver-ready-card-contract/`;
  card remains in `3.inprogress` for independent review.
- 2026-08-01T21:44:22Z release baseline passed 26/26; payload ready for
  independent review.
- 2026-08-01T21:53:14Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
