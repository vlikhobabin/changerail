## Context

Affected v7 был создан clean от published authorization и сохранил корректную
RED chronology, но terminal cycle-2 review оставил три blocker classes:
registry targets выводились эвристически, AST oracle не замыкал bindings и
indirect execution, а часть counterfactual proof не меняла фактический
production guard через наблюдаемый public boundary. Admission и proof
connectivity уже были предметом linked rescues в этой lineage, поэтому ещё
одна implementation patch запрещена до отдельного investigation/design этапа.

Latest safe source — published v7 authorization tip
`72541e3e9e906000922829629026d45bc77ae078`. Terminal v7 code, tests, card,
manifest, verdict files, logs и raw evidence не являются implementation input;
эта decision переносит только concise blocker chronology.

## Goals / Non-Goals

**Goals:**

- определить исчерпывающий typed source-of-truth для всех registry targets;
- замкнуть Python import binding, call ownership и semantic execution inventory;
- сделать каждый обязательный counterfactual source-connected и наблюдаемым
  через public production boundary;
- сохранить exact 35→30 profile, full-only authority и все ранее опубликованные
  fail-closed boundaries;
- разрешить только порядок decision → authorization v8 → clean implementation
  v8 → certification.

**Non-Goals:**

- исправлять или публиковать terminal v7 payload;
- создавать v8 authorization/implementation card, code, tests или workflow;
- запускать history, real full/affected, benchmark, live matrix или
  certification checks;
- ослаблять scheduler-v1, full-release authority или 499-LOC implementation
  ceiling.

## Decisions

### 1. Typed registry является единственным target inventory

Future v8 хранит frozen immutable entries, где каждый execution operand имеет
declared kind: `executable`, `module`, `script`, `file`, `directory` или
`embedded-command`. Admission не угадывает kind по suffix, наличию slash или
существованию path. Она независимо извлекает operands из всех 30 physical
tasks, сравнивает multiset typed identities с frozen registry и отклоняет
missing, extra, duplicate ambiguity, root, escape, wrong kind и invalid
normalized identity до Git/scheduler/filesystem mutation.

Альтернатива — продолжать поддерживать отдельный `PHYSICAL` плюс эвристический
`FROZEN_TARGETS` — отклонена: два источника расходятся и оставляют embedded или
root operands неохваченными.

### 2. Ownership проверяется как bindings плюс closed execution graph

Oracle разрешает только exact unaliased imports и связывает imported name с
конкретным authorized call site. Runner имеет закрытый top-level AST shape и
единственный guarded вызов profile `main`; profile имеет один direct
`run_plan`; scheduler имеет один direct broker activation. Star/module imports,
aliases, shadowing, assignment/rebinding, wrappers, attribute calls и duplicate
calls fail closed.

Отдельный execution inventory перечисляет все разрешённые raw process launch
sites и доказывает, что semantic commands исполняются только через typed
scheduler chain. Дополнительный `subprocess`, `os.system`, `exec`/`eval`,
module-qualified call или individual semantic command вне chain отклоняется,
даже если canonical call всё ещё присутствует.

Альтернатива — считать строки imports и calls независимо — отклонена: она не
доказывает, что вызван именно импортированный symbol, и не замечает параллельный
indirect execution surface.

### 3. Counterfactual меняет source, а не test wiring

Для каждого named guard proof строит isolated fixture из published source,
применяет одну bounded source/AST mutation к фактическому guard и запускает
public runner/oracle. Canonical neighbor обязан пройти, mutant обязан изменить
ровно intended outcome, а fixture отдельно доказывает, что все preceding guards
удовлетворены. Patch функции guard, constant override, locally reimplemented
assertion или earlier injected failure не считается connected proof.

Это относится к typed targets, origins, selector bounds, runtime ordering,
scheduler schema/cross-fields, authority states, protocol artifacts и closed
ownership/execution mutants.

### 4. Чистая v8 lineage получает отдельную authorization

Decision публикует только six-field investigation object для future v8.
Authorization v8 будет отдельным docs-only reviewed commit; только после него
может появиться clean implementation, использующая exact two-field reference.
V8 начинается от authorization-publishing HEAD, не импортирует v7 и остаётся
в пределах 499 added production LOC.

## Risks / Trade-offs

- [Risk] Closed AST shape может быть слишком хрупким к harmless refactor →
  mitigation: замыкать security/authority-relevant bindings и execution sites,
  а не форматирование или source locations.
- [Risk] Typed registry продублирует часть task metadata → mitigation: одна
  immutable typed structure генерирует scheduler tasks и admission inventory;
  independent extraction остаётся verifier, а не вторым authoring source.
- [Risk] Source-mutant fixtures дороже unit mocks → mitigation: inventory
  bounded, static/current-only и не запускает real affected/full semantics.
- [Risk] 499 LOC требует упрощения → mitigation: authorization допускает
  `301..500`, но preflight считает production LOC и блокирует `>=500`.

## Migration Plan

1. Опубликовать эту docs-only decision от exact safe v7 authorization tip.
2. Отдельно опубликовать exact bounded authorization v8.
3. Создать clean v8 worktree от authorization-publishing HEAD и доказать
   retained pre-production RED до executable/main-spec mutation.
4. Реализовать typed registry, closed execution graph и source-mutant proof;
   выполнить только allowed focused/static/current checks.
5. После fresh Sol/high `GO` опубликовать v8; только затем открыть final
   critical certification.

Rollback для этого этапа — не создавать authorization successor. Published
decision не меняет executable behavior.

## Open Questions

- none; exact v8 contract и запрещённые alternatives зафиксированы выше.
