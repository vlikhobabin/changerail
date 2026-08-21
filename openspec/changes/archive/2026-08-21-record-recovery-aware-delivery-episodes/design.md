## Context

Single-card statuses идентифицируются `run_id`, plan status хранит child run
references, review history индексируется по card id, а publish result находится
в delivery manifest. Current metrics соединяет эти источники по card id и
timestamps, поэтому ранний preflight может получить review history более
позднего delivery. Manual recovery без runner status вообще выпадает.

`PerformanceCollector` сохраняет общие command count/event counts, но details
ограничены последними 50 commands и 100 timeline events без явного sampling
contract. Progress и external-blocker changes дают структурированные phase и
recovery transitions, на которых можно построить durations и lineage.

## Goals / Non-Goals

**Goals:**

- Дать каждой card execution stable episode identity и каждой lifecycle попытке
  unique attempt identity.
- Связать runner, plan, review history и manifest explicit ids.
- Сохранять totals независимо от bounded detail samples.
- Материализовать canonical public-safe episode record в ignored runtime state.
- Оставить legacy records читаемыми с `unknown`, не придумывая ложные связи.

**Non-Goals:**

- Не сохранять prompts, command bodies, MCP args/results или screenshots.
- Не заменять live heartbeat, resume authorization или business acceptance.
- Не делать tracked episode ledger.
- Не восстанавливать точную историю legacy run из raw logs.

## Decisions

1. **Episode id создается при первой executable попытке и наследуется.** Новый
   single-card/plan child получает `episode_id` до preflight. Resume обязан
   взять id из schema-valid source status; новый unrelated run той же карточки
   получает другой id. Plan card entry хранит текущий episode id.

2. **Attempt identity явна и не подменяет `run_id`.** Каждый source artifact
   хранит `attempt` с `id`, `kind`, optional `parent_attempt_id` и
   `previous_attempt_id`. Для runner process `attempt.id` равен `run_id`, что
   избегает второго генератора. Review cycles и publish получают отдельные ids
   в своих owner artifacts; rescue ссылается на review, который его вызвал.
   Kinds ограничены `preflight`, `delivery`, `recovery`, `review`, `rescue`,
   `publish`.

3. **Owner artifacts остаются authoritative, episode record — derived index.**
   Delivery status владеет process timing/usage, review history — findings и
   cycle outcome, manifest — publish. Runner-owned helper идемпотентно
   материализует `changerail.delivery-episode.v1` под ignored runtime root,
   объединяя только schema-valid sources с совпадающими workspace/card/episode
   ids. Attempt ids уникальны; conflicting duplicate blocks refresh. Это
   устраняет второй mutable source of truth.

4. **Lineage — граф с двумя ограниченными связями.** `parent_attempt_id`
   обозначает причинный owner (например review для rescue),
   `previous_attempt_id` — последовательность attempts одного kind/continuation.
   Ссылки обязаны указывать на attempt того же episode или оставаться absent.
   Свободные labels и inferred timestamp links не используются.

5. **Totals и samples разделены.** Performance пишет aggregate counts и total
   durations для всех command/tool classes, phase durations и wait kinds.
   `samples` остаются bounded и содержат только sanitized labels. Record явно
   указывает `observed_count`, `retained_count`, limit и truncation. Это
   сохраняет стоимость long run после удаления ранних details.

6. **Waits приходят только из structured transitions.** Progress phase/stage
   дает active/wait intervals; external blocker и explicit operator-wait event
   дают bounded wait class. Entered values и external response contents не
   являются полями. Interval без корректной closing event учитывается как
   `unknown/incomplete`, а не как guessed active time.

7. **Legacy compatibility — isolated synthetic episode.** Reader может показать
   legacy run как episode, derived только из его `run_id`, но не присоединяет
   review/manifest по card id без explicit lineage. Missing fields остаются
   `unknown`; существующие v1 schemas получают optional additions.

## Risks / Trade-offs

- [Несколько writers обновляют runtime рядом] -> каждый пишет owner artifact,
  episode refresh использует atomic write и conflict detection.
- [Clock skew и незакрытые intervals] -> timestamps не определяют lineage;
  durations получают incomplete marker.
- [Record size grows] -> attempt summaries bounded, detailed evidence остается
  по indirect paths.
- [Legacy metrics become less complete] -> лучше explicit unknown, чем неверно
  связанный later review.

## Migration Plan

1. Добавить optional episode/attempt fields в owner schemas.
2. Обновить runner, review history writer и publish manifest writer.
3. Добавить aggregate totals/sampling metadata и structured wait events.
4. Добавить episode refresh helper и contract fixtures.
5. После rollout metrics переходит на explicit lineage; rollback продолжает
   читать old optional-less records.

## Open Questions

- none
