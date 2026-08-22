## Context

Verification floor сейчас собирается из `AGENTS.md`, `openspec/config.yaml`,
OpenSpec `tasks.md`/`design.md` и затронутого toolchain. Delivery сохраняет
command outcomes/evidence index, manifest хранит summary, reviewer заполняет
verdict по каждому acceptance criterion. Эти поверхности фиксируют требования,
но не дают детерминированного ответа: для данного changed surface все ли
известные invariants получили oracle и evidence.

Field validation дала достаточное основание для нового contract: critical
deliveries дошли до independent review, где обнаружились непроверенный positive
route, assertion вне published timeout boundary и proof через disconnected
renderer/form paths. Значит, существующая дисциплина evidence полезна, но одна
agent inference до review допускает повторяемый false-green.

## Goals / Non-Goals

**Goals:**

- Добавить минимальную optional project-owned coverage map.
- Связать generic changed paths/surface kinds с invariant, oracle и required
  evidence без копирования acceptance/tasks.
- Дать domain extensions namespaced surface boundary.
- Подготовить tracked plan reference и ignored runtime ledger contracts для
  deterministic reconciliation.
- Сохранить текущий workflow без изменений в проектах, где map не настроена.

**Non-Goals:**

- Не копировать Orca reliability catalog и не задавать global test matrix.
- Не добавлять BSL, metadata, managed-form или 1C tools в generic core.
- Не считать path match доказательством invariant.
- Не заменять OpenSpec acceptance/tasks, evidence index или review verdict.

## Decisions

1. **Map — отдельный tracked project file, referenced from OpenSpec config.**
   Default path `.changerail/verification-coverage.yaml` включается только через
   `verification.coverage_map` в `openspec/config.yaml`. Это сохраняет config
   source of policy и позволяет independently schema-validate растущую карту.
   Embed всех entries прямо в config отвергнут как неудобный для extensions;
   runtime-only map отвергнута как непроверяемая policy.

2. **Per-entry модель ограничена пятью полями.**
   `changerail.verification-coverage.v1` содержит entries с `id`, `applies_to`,
   `invariant`, `oracle`, `required_evidence`. `applies_to` допускает normalized
   POSIX globs, operation kinds и namespaced `surface_kinds`; как минимум один
   selector обязателен. `oracle` — bounded `{kind, ref}`, а
   `required_evidence` — массив `{kind, oracle_ref}`. Не добавляются owner,
   severity, maturity, promotion или soak fields: риск и обязательность уже
   принадлежат card/project policy.

3. **Surface kinds are opaque namespaced data.** Generic core знает только
   path/operation matching и принимает surface ids формата `<namespace>.<kind>`
   из schema-valid extension-produced scope. Будущая 1С-интеграция может
   объявить BSL, metadata, managed forms, roles, posting, reports, migrations и
   runtime UI как свои ids; ChangeRail не понимает их semantics и не запускает
   domain tools самостоятельно.

4. **Planning reference не дублирует правило.** Если map включена, `ff` создает
   per-change `verification-coverage.json` со schema id, map fingerprint,
   selected coverage ids и SHA-256 exact card acceptance criteria. Invariant,
   oracle, command и criterion text не копируются. Artifact является tracked
   declaration того, что план учел; source rule остается map, acceptance — card.

5. **Runtime ledger is derived and fingerprint-bound.** Ignored
   `changerail.verification-coverage-ledger.v1` ссылается на map/plan
   fingerprints, card/change, manifest scope and reviewed-tree fingerprint. Его
   entries содержат coverage id, applicability, oracle observation state и
   evidence-index refs. Ledger не выдает final pass; reviewer verdict остается
   authority по acceptance.

6. **Matching is deterministic but not an oracle.** Glob/operation/surface
   selectors только делают entry applicable. Состояние `covered` возможно лишь
   после schema-valid observed evidence, связанного с declared oracle. Один
   path match никогда не дает pass.

7. **Решение реализовывать contract принято из-за field evidence.** Вариант
   оставить только current tasks/skills дешевле, но не может детерминированно
   отличить «все известные commands прошли» от «один known invariant не был
   выбран». Новые schemas оправданы при optional rollout и отсутствии default
   global gates.

## Risks / Trade-offs

- [Map становится параллельным backlog требований] -> entries не содержат
  acceptance status/tasks и обязаны ссылаться на stable oracle refs.
- [Stale selectors дают ложное спокойствие] -> map/plan/manifest fingerprints и
  uncovered-surface diagnostic fail closed при configured map.
- [Domain extension leaks into core] -> только namespaced ids and data contract;
  classifiers/oracles принадлежат extension/project.
- [Configuration burden] -> map optional, generic Python example minimal, no
  implicit generated gates.

## Migration Plan

1. Добавить map, plan and ledger schemas plus inventory fixtures.
2. Добавить optional config reference/template guidance.
3. Добавить generic Python example и invalid selector/oracle fixtures.
4. Enforcement включить отдельным dependent change.
5. Rollback удаляет config reference; current verification floor remains.

## Open Questions

- none
