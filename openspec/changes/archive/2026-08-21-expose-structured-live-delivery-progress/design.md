## Context

`bin/changerail-delivery-runner` атомарно пишет
`changerail.delivery-run.v1`, но после запуска child обновляет record только при
старте процесса и terminal outcome. `PerformanceCollector` читает structured
Codex JSONL для итоговой telemetry, однако поддерживаемый status не должен
раскрывать значения из этих событий. Queue status копирует только состояние
`running` и ссылку на child status.

Из одного generic Codex event envelope нельзя достоверно вывести переходы
`ff -> do -> review -> publish`. Эти переходы знает lifecycle skill, поэтому
нужен явный value-free event transport. Runner при этом должен оставаться
единственным writer канонического `status.json`.

## Goals / Non-Goals

**Goals:**

- Публиковать bounded, schema-backed progress и heartbeat для single-card и
  aggregate status.
- Получать major transitions из lifecycle, а activity heartbeat — из наличия
  валидных Codex event envelopes без чтения их payload values.
- Обнаруживать stale heartbeat отдельно от terminal classification.
- Сохранить v1 compatibility и ignored raw evidence.

**Non-Goals:**

- Не выводить этап из текста agent messages, shell commands или output.
- Не превращать stale heartbeat в автоматическое убийство child.
- Не гарантировать процент выполнения или оставшееся время.
- Не переносить raw runtime events в tracked artifacts.

## Decisions

1. **Runner остается единственным status writer.** Для run создается ignored
   append-only event file рядом с `stdout.jsonl`. Lifecycle helper записывает
   туда только `schema`, `run_id`, `card_id`, `phase`, `stage`, sequence и
   timestamp. Runner валидирует identity, enum и монотонность, затем атомарно
   обновляет `status.json`. Прямое редактирование status дочерним процессом
   отвергнуто из-за lost updates и возможности подменить terminal fields.

2. **Progress contract использует один объект
   `changerail.delivery-progress.v1`.** Обязательные поля: `phase`, `stage`,
   `heartbeat_at`, `event_counter`. Phase ограничен lifecycle значениями
   `preflight`, `ff`, `do`, `review`, `publish`, `terminal`; stage —
   `starting`, `discovery`, `planning`, `implementation`, `verification`,
   `waiting`, `finalizing`, `complete`. Дополнительные prose/value fields схема
   запрещает. Один object используется в child и aggregate records, чтобы не
   появилось двух семантик.

3. **Heartbeat не парсит event payload.** Runner считает activity только по
   успешно разобранному top-level Codex JSON object и не переносит его поля в
   progress. Status write coalesced до документированного интервала; major
   lifecycle event записывается сразу и увеличивает `event_counter`. Таким
   образом обычная активность обновляет время, а переходы остаются явными.

4. **Staleness вычисляется при чтении/обновлении status.** Diagnostic содержит
   bounded health (`active`, `stale`, `terminated`), heartbeat age и observed
   process state. Один пропущенный интервал дает только `stale`; terminal result
   определяется существующим process/terminal protocol. Отдельный watchdog с
   mutation authority не добавляется.

5. **Queue копирует validated child progress.** Перед mirror runner читает
   schema-valid child status, сверяет run/card identity и копирует только
   `progress` и bounded health в соответствующий `cardStatus`. Raw paths, logs
   и errors по-прежнему остаются indirect references.

6. **Lifecycle sources обновляются вместе.** Canonical skills под `skills/` —
   source of truth; Claude wrappers и repo-local symlinks проверяются drift
   smoke. Consumer-specific phase names не расширяют enum и отображаются на
   ближайший generic stage.

## Risks / Trade-offs

- [Child активен внутри долгой команды, но JSONL молчит] -> status может стать
  `stale`; diagnostic остается advisory и учитывает живой process.
- [Child пишет forged event] -> identity, schema и sequence проверяются, а
  event не имеет terminal или mutation authority.
- [Частые события создают I/O] -> heartbeat writes coalesced, transitions
  записываются немедленно.
- [Legacy consumers не знают `progress`] -> поле optional в v1 schemas и не
  меняет terminal semantics.

## Migration Plan

1. Расширить обе schemas optional progress/health definitions.
2. Добавить event transport и coalesced status updates в runner.
3. Научить lifecycle skills отправлять major transitions.
4. Добавить aggregate mirror, status rendering и focused smokes.
5. Обновить docs; rollback удаляет optional writer/reader paths, сохраняя
   прежние v1 records валидными.

## Open Questions

- none
