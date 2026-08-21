## Context

`bin/changerail-delivery-metrics` scans every delivery-run status, indexes one
review history per card id and applies that history to every run row for the
card. Preflight statuses enter run denominators, manual/recovery attempts are
not rolled up, and plan metrics only list child run ids. The episode contract
provides explicit identity and attempt kinds; metrics must consume it without
changing runtime authority.

## Goals / Non-Goals

**Goals:**

- Report one primary row per delivery episode with optional attempt detail.
- Exclude preflight-only episodes from delivery/review-rate denominators.
- Join review and publish only through explicit episode lineage.
- Sum recovery cost and complete aggregate telemetry with clear unknowns.
- Preserve a bounded legacy view without false associations.

**Non-Goals:**

- Не оценивать product acceptance по process telemetry.
- Не читать raw JSONL для восстановления отсутствующих fields.
- Не изменять owner runtime artifacts или переписывать legacy records.
- Не превращать missing optional usage в zero.

## Decisions

1. **Episode record — preferred input, owner artifacts — validated fallback.**
   Metrics сначала читает `changerail.delivery-episode.v1`. Если index
   отсутствует, он может детерминированно собрать explicit-lineage sources in
   memory. Card-id-only join запрещен. Legacy run становится isolated row.

2. **Denominators use executable episode classification.** Episode участвует в
   delivery success только при attempt kind `delivery` или `recovery`.
   Preflight-only plan/run показывается отдельным count, но не снижает success
   или first-pass-review rate. First-pass review определяется первым linked
   review attempt именно этого episode.

3. **Final outcome is explicit.** `delivered` требует linked successful publish
   или terminal delivered attempt по compatibility contract. Abandoned,
   blocked и no-go не переопределяются later card history. Conflicting terminal
   owners дают `invalid`, а не выбираются по timestamp.

4. **Durations and usage are additive with overlap guard.** Metrics суммирует
   attempts, но episode wall time идет от первого start до explicit end. Active,
   wait и operator-wait totals используют owner aggregates; duplicate attempt
   id не считается дважды. Missing fields остаются string `unknown` в text/CSV
   и `null` плюс availability marker в JSON.

5. **Output remains backward-usable.** Text показывает episode summary и
   attempt count; JSON получает `episodes`, `attempts`, `aggregate`; CSV по
   умолчанию one row per episode, optional `--attempts` дает attempt rows.
   Existing per-run fields сохраняются в legacy/attempt mode на migration
   interval.

## Risks / Trade-offs

- [Rates change after preflight exclusion] -> docs называют denominator и
  fixture фиксирует old/new difference.
- [Incomplete episode owner artifacts] -> row remains visible with unknown and
  diagnostics, not silently dropped.
- [Attempt intervals overlap] -> wall time and additive active totals reported
  separately with overlap diagnostic.

## Migration Plan

1. Добавить episode collector and validator.
2. Перевести joins/denominators на explicit lineage.
3. Добавить JSON/text/CSV outputs и legacy flags.
4. Расширить synthetic metrics fixtures and docs.
5. Rollback сохраняет old collector, не меняя episode records.

## Open Questions

- none
