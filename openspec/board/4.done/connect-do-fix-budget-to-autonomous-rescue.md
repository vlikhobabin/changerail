# Связать исчерпание fix budget с автономным rescue flow

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Диагностика consumer delivery run 2026-07-18: `changerail-do` исчерпал
  default `--max-fix-cycles 2` до independent review, а внешний runner
  классифицировал exit code `0` как `DELIVERED`.
- `skills/changerail-do/SKILL.md`
- `skills/changerail-deliver/SKILL.md`
- `bin/changerail-delivery-runner`

## Summary
Закрыть разрыв между pre-review fix budget и autonomous repeated-`NO-GO`
policy. Исчерпание `changerail-do --max-fix-cycles` не должно превращаться в
ручной запрос на увеличение budget или ложный `DELIVERED`: bounded локальный
дефект должен получить детерминированный scoped continuation, а scope-expanding
или отдельная работа — linked rescue/replacement card, поставленную перед
заблокированным downstream plan.

## Acceptance
- `changerail-do` при исчерпании fix budget завершает фазу machine-readable
  non-delivered outcome с reason `fix_budget_exhausted`; свободный текст и exit
  code `0` не могут превратить safety stop в `DELIVERED`.
- `changerail-deliver` различает bounded in-scope micro-fix и работу, требующую
  отдельного scope: первая остаётся ограниченным same-card rescue, вторая
  создаёт linked rescue/replacement card с lineage и ставит её перед blocked
  downstream work без запроса exceptional manual authorization по умолчанию.
- External/unavailable blockers остаются `BLOCKED`/`NOT-VERIFIABLE` и не
  порождают бессмысленную implementation-card chain.
- Queue runner не продолжает downstream cards после fix-budget safety stop и
  умеет возобновить original plan только после published recovery card с fresh
  independent `GO`.
- Exit code `0` без structured terminal event и без опубликованной карточки не
  классифицируется как `DELIVERED`.
- Smoke coverage включает: fix-budget exhaustion, bounded micro-fix,
  rescue-card insertion/order, external blocker и exit-0 non-published child.
- Skills, methodology, specs, contract docs и consumer templates используют
  одну терминологию и не смешивают `max-fix-cycles` с review `NO-GO` cycles.

## Change Set
- `define-fix-budget-rescue-semantics`
- `enforce-fix-budget-terminal-and-recovery`

## Verify
- `python3 -m py_compile bin/changerail-delivery-runner && python3 scripts/smoke-delivery-runner.py` - passed; covers fix-budget marker parsing, unpublished exit `0`, marker-like prose, external blocker, missing child status and recovery resume ordering.
- `python3 scripts/smoke-contract-schemas.py` - passed; validates optional `terminal_reason`, `recovery_for`, `recovered_by` and recovery status fixtures.
- `python3 scripts/smoke-bootstrap-project.py` - passed, 5/5.
- `python3 scripts/smoke-wiring-discovery.py` - passed, 168/168.
- `./bin/openspec validate enforce-fix-budget-terminal-and-recovery --strict` - passed before archive.
- `./bin/openspec validate --all --strict` - passed after archive, 13/13.
- `python3 -m json.tool .mcp.json` - passed.
- TOML parse for `.codex/config.toml` - passed with `TOML_OK`.
- `git diff --check` - passed.
- `python3 scripts/public-surface-scan.py` - passed, 489 files scanned, 0 findings.
- `python3 scripts/run-release-baseline.py` - passed, 25/25 release gates.

## Archive
- `openspec/changes/archive/2026-07-18-define-fix-budget-rescue-semantics/`
- `openspec/changes/archive/2026-07-18-enforce-fix-budget-terminal-and-recovery/`

## Related
- `skills/changerail-do/SKILL.md`
- `skills/changerail-deliver/SKILL.md`
- `bin/changerail-delivery-runner`
- `scripts/smoke-delivery-runner.py`
- `openspec/specs/changerail-agent-methodology/spec.md`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `openspec/specs/changerail-skill-surface/spec.md`
- `openspec/board/4.done/fix-delivery-runner-safety-stop-outcome.md`

## Result
Implemented and verified. `changerail-do`/`changerail-deliver` now share the
`fix_budget_exhausted` handoff semantics; the delivery runner preserves
`terminal_reason`, fails closed for unpublished exit `0`, stops queues on
fix-budget exhaustion or invalid child status, and supports constrained
`recovery_for` resume ordering before downstream work.

Published reviewed payload as `07007f5ea7f6119a2e46ec0c1bd4a97f5f934167`; push status `pending` on `main`/`origin`.

## Next
- done

## Change 1: `define-fix-budget-rescue-semantics`

### Why
`changerail-do` и autonomous review rescue loop используют разные budgets, но
текущий contract не определяет переход из pre-review fix-budget exhaustion в
supervised `changerail-deliver` continuation.

### Goal
Определить единый observable contract для bounded same-card micro-fix, linked
rescue/replacement и external blocker без смешивания fix cycles с review
`NO-GO` cycles.

### Scope
- `AGENTS.shared.md`, lifecycle skills и public methodology docs.
- Main OpenSpec capabilities для agent methodology и skill surface.
- Bootstrap consumer guidance и соответствующий wiring/bootstrap smoke.

### Acceptance
- Fix-budget exhaustion имеет machine-readable non-delivered reason и не
  предлагает exceptional manual budget как default path.
- Bounded local micro-fix, scope-expanding recovery и external blocker имеют
  разные детерминированные ветви.
- Consumer guidance явно различает `max-fix-cycles` и `max-review-cycles`.

### Depends On
- none

### Related
- `openspec/changes/define-fix-budget-rescue-semantics/`

## Change 2: `enforce-fix-budget-terminal-and-recovery`

### Why
Одних agent instructions недостаточно: внешний runner сейчас может вывести
`DELIVERED` для exit code `0`, хотя карточка не опубликована и worker завершил
fix-budget safety stop.

### Goal
Сделать non-delivered classification и recovery ordering проверяемыми runner
contracts и smoke tests.

### Scope
- `bin/changerail-delivery-runner` и focused smoke coverage.
- Main runner/contracts specs и contract docs.
- Fail-fast queue behavior и resumable recovery ordering.

### Acceptance
- Exit code `0` без structured outcome и без published card даёт `BLOCKED`, не
  `DELIVERED`.
- Structured fix-budget exhaustion останавливает downstream queue.
- Linked recovery card фиксируется перед blocked downstream work, а original
  plan возобновляется только после её published fresh `GO`.

### Depends On
- `define-fix-budget-rescue-semantics`

### Related
- `openspec/changes/enforce-fix-budget-terminal-and-recovery/`

## Log
- 2026-07-18T16:01:49Z card created from a reproduced gap between
  `max-fix-cycles`, autonomous rescue policy and runner terminal classification.
- 2026-07-18T16:04:00Z story accepted into `2.todo` and decomposed into
  methodology/skill semantics followed by runner enforcement.
- 2026-07-18T16:13:00Z both ordered changes received valid apply-ready
  proposal, design, delta-spec and task artifacts; card moved to `3.inprogress`.
- 2026-07-18T16:30:00Z implementation completed in ChangeRail core: lifecycle
  semantics, runner enforcement, schemas, smoke coverage, docs/templates and
  main specs updated; both OpenSpec changes archived after passing verification.
- 2026-07-18T16:34:00Z one release-baseline lint finding was fixed in scope;
  the repeated full baseline passed all 25 gates.
- 2026-07-18T17:06:53Z publish finalized card into `4.done` with commit `07007f5ea7f6119a2e46ec0c1bd4a97f5f934167` and push status `pending`.
