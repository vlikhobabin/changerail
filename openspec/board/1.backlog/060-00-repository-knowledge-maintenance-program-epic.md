# Серия 060: Repository knowledge и maintenance harness

## Status
1.backlog

## Owner
ChangeRail core

## OpenSpec Stage
epic

## Series
`060-repository-knowledge-maintenance`

## Series Index
`00`

## Planning State
series baseline captured; executable cards remain in `1.backlog` until their
dependency and readiness gates pass

## Delivery Mode
coordination-only; не запускать `$chrl-deliver` для этой epic-карточки

## Source
- [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)
- [An open-source spec for Codex orchestration: Symphony](https://openai.com/index/open-source-codex-orchestration-symphony/)
- [Codex: Update documentation](https://learn.chatgpt.com/use-cases/update-documentation)
- [Codex: AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Codex: Refactor your codebase](https://learn.chatgpt.com/use-cases/refactor-your-codebase)
- [Codex scheduled tasks](https://learn.chatgpt.com/docs/automations)
- [Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode)
- [Codex GitHub Action](https://learn.chatgpt.com/docs/github-action)
- [Diataxis documentation framework](https://diataxis.fr/)
- [C4 model](https://c4model.com/)
- [ArchUnit user guide](https://www.archunit.org/userguide/html/000_Index.html)
- [GitHub Actions scheduled workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)

## Summary
Добавить в ChangeRail опциональный scheduler-neutral maintenance harness,
который делает repository knowledge проверяемым инженерным контрактом,
нормализует deterministic и agent-triaged findings и передает принятые
исправления в обычный review-gated ChangeRail delivery pipeline.

```text
repository signals -> deterministic scan -> structured report
  -> bounded agent triage -> deduplicated ChangeRail card
  -> ff -> do -> independent review -> pub
```

Эта epic фиксирует общий контракт, порядок и safety boundaries. Она не является
единицей реализации и не заменяет OpenSpec planning, independent review,
delivery runner или consumer-owned repository policy.

## Program Goal
- Дать consumer репозиторию tracked catalog и policy overlay без навязывания
  структуры `docs/` или конкретного языка реализации.
- Сделать deterministic knowledge checks доступными в PR/CI без LLM.
- Отделить raw scan evidence, agent triage и repository mutation.
- Не создавать повторные cards для одной finding identity.
- Поддержать bounded scheduled operation без commit, push, publish, deployment
  или destructive cleanup по умолчанию.

## Frozen Architecture Decisions
- Knowledge catalog живет в tracked `.changerail/knowledge.yaml`, policy overlay
  в `.changerail/maintenance.yaml`, baseline/waivers в tracked
  `.changerail/maintenance-baseline.yaml`.
- YAML сначала разбирается structured parser-ом, затем валидируется публичными
  JSON Schemas; ad hoc line parsing не является contract implementation.
- Runtime reports, run history, locks, prompts и raw evidence живут только под
  ignored `.runtime/changerail/maintenance/`.
- Finding identity fingerprint вычисляется отдельно от evidence fingerprint.
  Новое evidence обновляет существующую finding, а не создает новую identity.
- Ignored state сохраняет `first_seen` и историю только при сохраненном state
  backend. Ephemeral scheduler без восстановленного state не получает
  exactly-once гарантию; durable card dedup обеспечивается fingerprint-marker-ом
  в tracked board cards.
- `scan` и default skill mode read-only. `render-index`, baseline acceptance,
  card creation и fix требуют отдельных explicit write flags.
- CLI не выполняет LLM triage. Agent skill создает schema-bound annotations,
  которые CLI может проверить и превратить в preview или explicit card write.
- Native detector adapters получают argv array, repository cwd, timeout и
  schema-bound JSON output; shell interpolation и language-specific analyzers в
  generic core не входят.
- `verify-project` проверяет только opt-in wiring/config/schema/ignore contract.
  Repository scan остается отдельным helper-ом; workspace drift gate и delivery
  runner не поглощают maintenance semantics.
- Карточка `050-harden-greenfield-consumer-bootstrap` владеет threshold и
  remediation для generated AGENTS instruction budget. Серия `060` только
  импортирует такой check как finding после появления стабильного producer
  contract.
- Новый public helper обязан иметь POSIX и native Windows `.cmd` entrypoints,
  generated-copy wiring coverage и platform-neutral smoke fixtures.

## Common Constraints
- Public schemas используют namespace `changerail.*` и не меняют frozen ids
  существующих review, delivery или evidence contracts.
- Tracked catalog, policy, baseline, cards, docs и fixtures должны быть
  repository-relative и public-safe.
- Raw file contents, absolute consumer paths, credentials, runtime dumps и
  private evidence не копируются в tracked findings или cards.
- Diataxis и C4 являются поддержанными classifications/guidance, но не задают
  обязательную directory layout или полный набор диаграмм.
- Architecture fitness реализуется через generic adapter protocol; ArchUnit,
  import-linter, dependency-cruiser и custom checkers остаются consumer-owned.
- GitHub schedule и другие schedulers рассматриваются как at-least-once и могут
  задерживать либо пропускать run; core не полагается на точный cron или
  process-local state.
- Ни один scheduled default не меняет repository или external systems.
- Возраст файла сам по себе не является evidence для удаления.

## Series Cards
1. `060-01-establish-repository-knowledge-contract.md`
2. `060-02-add-deterministic-knowledge-integrity-gate.md`
3. `060-03-add-maintenance-findings-lifecycle.md`
4. `060-04-add-maintain-skill-and-scheduler-adapters.md`
5. `060-05-connect-feedback-and-quality-rollup.md`
6. `060-06-add-scoped-maintenance-fix-mode.md`

## Dependency Order
- `060-01` не имеет series dependencies.
- `060-02` зависит от catalog/policy contract из `060-01`.
- `060-03` зависит от stable detector output из `060-02`.
- `060-04` зависит от report/state/card contracts из `060-03`.
- `060-05` зависит от structured lifecycle из `060-03` и operational surface
  из `060-04`.
- `060-06` зависит от quality evidence из `060-05` и отдельного fix-mode
  readiness decision.

## MVP Exit Gate
- Cards `060-01`..`060-03` опубликованы через обычный ChangeRail flow.
- ChangeRail dogfood catalog проходит schema validation и deterministic scan.
- Broken local link/anchor, orphan record, stale generated index и duplicate
  card fixtures дают ожидаемые schema-backed findings.
- Повторный scan со стабильным state сохраняет finding identity и `first_seen`;
  измененное evidence меняет только evidence fingerprint.
- Audit/scan defaults не меняют tracked или external state.

## Program Exit Gate
- Cards `060-01`..`060-05` опубликованы, либо каждая закрыта с replacement или
  explicit out-of-scope rationale.
- `060-06` реализована только после положительного fix-mode readiness gate;
  иначе остается backlog story без ослабления audit/triage value.
- POSIX, native Windows entrypoints, bootstrap opt-in, verifier diagnostics,
  scheduler examples и public-safety checks согласованы.
- Existing `ff -> do -> review -> pub` contracts и consumer repositories
  остаются обратно совместимыми.

## Related
- `AGENTS.shared.md`
- `README.md`
- `docs/changerail-contracts.md`
- `docs/changerail-source-of-truth-architecture.md`
- `openspec/specs/changerail-drift-gate/spec.md`
- `openspec/specs/changerail-delivery-observability/spec.md`
- `openspec/board/1.backlog/050-harden-greenfield-consumer-bootstrap.md`

## Result
Planning baseline captured; implementation not started.

## Next
- Провести readiness review карточки `060-01`; после принятия переместить ее в
  `2.todo` и запустить `$chrl-deliver` или explicit `$changerail-ff`.

## Log
- `2026-08-09T11:41:01Z` — создана исходная broad implementation card по
  результатам исследования Harness Engineering и maintenance practices.
- `2026-08-09T12:35:25Z` — исходная card преобразована в coordination epic;
  зафиксированы architecture decisions, MVP boundary и шесть executable stories.
