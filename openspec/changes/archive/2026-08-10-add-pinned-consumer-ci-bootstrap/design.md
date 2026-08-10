## Context

ChangeRail release CI проверяет собственные templates, но generated consumer не
получает runnable CI. Для первого consumer pipeline оператор вручную выбирает
ChangeRail revision, checkout topology и verification commands.

## Goals / Non-Goals

**Goals:**
- генерировать opt-in CI из tracked template;
- использовать exact strict consumer lock;
- доказать clean-clone behavior в arbitrary consumer checkout path;
- не требовать Codex credentials для baseline.

**Non-Goals:**
- автоматически публиковать consumer repository;
- поддерживать branch/range/floating ChangeRail references в CI;
- генерировать provider-specific deployment jobs.

## Decisions

### Explicit CI opt-in

`--with-ci` генерирует `.github/workflows/changerail-consumer-verify.yml`.
Опция требует strict `changerail.consumer-lock.v1`; advisory/no-lock combination
останавливается до target mutation.

### Exact checkout and repair

Workflow читает schema/version/revision, checkout-ит canonical ChangeRail source
at exact revision под runner temporary directory и выполняет lock-driven wiring
repair в disposable consumer checkout. Затем он запускает
`bin/verify-project <consumer>` и consumer-declared baseline.

Это позволяет consumer checkout жить в произвольном runner path: tracked lock,
а не original sibling topology, определяет revision и owned repair plan.

### Credential boundary

Baseline не запускает delivery и не требует Codex auth. Workflow получает
`contents: read`, не имеет publish steps и не печатает repository credentials.

### Deterministic local smoke

Release smoke парсит workflow structured YAML, проверяет required triggers,
permissions, exact revision handoff и commands. Clean-clone fixture выполняет
тот же flow против local disposable Git repositories без network dependency.

## Risks / Trade-offs

- [GitHub-specific template narrows portability] -> GitHub Actions является
  первым explicit template; lock/commands остаются provider-neutral и docs
  описывают equivalent CI.
- [Repair makes disposable checkout dirty] -> gate подтверждает, что изменены
  только declared wiring paths; checkout не публикуется.
- [Canonical source unavailable] -> CI fails closed with revision/source
  diagnostic before verification.

## Migration Plan

1. Добавить template и bootstrap flag.
2. Добавить structured workflow smoke и local clean-clone fixture.
3. Включить smoke в release baseline/CI inventory.
4. Документировать lock refresh и failure remediation.

## Open Questions

- none
