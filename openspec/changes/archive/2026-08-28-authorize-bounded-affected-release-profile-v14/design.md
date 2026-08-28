## Context

Investigation v14 опубликована на exact commit
`c884971ccca3d4d6ab4d76f27c22122981131d16` и нормативно завершает terminal
v13 lineage. Она требует independently frozen descriptor identity,
non-following dangling-symlink admission, source/guard-bound scheduler proof и
public stream-complete rename/copy selection до любого executable v14.
Investigation остаётся decision source и не разрешает production mutation сама
по себе.

Authorization должна быть отдельным docs-only publish gate. Она связывает
один successor, ceiling и protocol allowance так, чтобы future preflight мог
проверить exact tracked `4.done` source. Terminal v13 card, code, tests, specs,
manifest, logs и raw evidence не являются входом; только уже опубликованные
contracts и их validated chronology доступны новой clean lineage.

## Goals / Non-Goals

**Goals:**

- опубликовать один exact six-field authorization object для implementation
  v14;
- зафиксировать единственный two-field reference, exact dependencies, sole
  downstream block и максимум `499` production LOC;
- перенести descriptor, runtime-root, scheduler-mutant и selector closure без
  ослабления;
- сохранить original RED chronology, independent Unicode/digest, direct
  connected activation и accumulated affected floor из published sources;
- оставить authorization dormant и docs-only до отдельного successor.

**Non-Goals:**

- создавать implementation card, focused test, production, CI или authority;
- читать или переносить terminal v13 payload/evidence;
- запускать history, full/affected baseline, benchmark, live matrix или
  certification;
- изменять full-only publication authority.

## Decisions

### 1. Authority задаётся одним exact object

Tracked authorization source содержит ровно:

```json
{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-exhaustive-guard-closure-v14.md","investigation_id":"investigate-affected-release-profile-exhaustive-guard-closure-v14","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v14.md","successor_id":"implement-bounded-affected-release-profile-v14","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Дополнительные keys, wrapper, alternate path/id, другой successor или ceiling
невалидны. Future implementation ссылается только на опубликованную card через
exact two-field object и начинается от authorization-publishing HEAD.

Альтернатива — наследовать executable authority непосредственно от
investigation — отклонена: complexity preflight требует отдельный clean
tracked `4.done` authorization source.

### 2. Descriptor и runtime admission являются независимым pre-semantic gate

Future implementation владеет immutable closed inventory всех literal command
tokens, effective-PATH executables, repository inputs и runtime outputs. Он
сравнивается bidirectionally с task registry и actual AST/source до probes,
Git, scheduler или mutation. Каждый Python/package-path/Ruff/Git/Node/npm/npx/
OpenSpec probe связан с exact descriptor; alternate usable command не
принимается.

Runtime paths инспектируются non-following primitive для root, каждого
ancestor, parent и leaf до missing-leaf branching. Dangling или resolving
symlink остаётся existing invalid directory entry; missing leaf допустим
только как exact direct child реального contained writable/searchable parent.

### 3. Scheduler и selector proof связаны с public source и guard order

Independent requirement-to-row и requirement-to-mutant maps покрывают каждый
valid reason tuple и top-level invariant. Каждый invalid case начинается от
соответствующего passing neighbor, меняет один field/source guard, проходит
public `profile.main` или `run_smoke` и доказывает actual AST/source mutation,
preceding guards и intended guard reachability.

Committed, staged и unstaged name-status streams независимо покрывают A/M/D и
R/C `000`, interior и `100` с обоими operands; untracked использует отдельный
NUL path stream. Grammar, framing, UTF-8, stream/aggregate bounds, path bounds,
unknown/self paths и resolved-base uncertainty дают exact 35-ID non-authority
fallback до semantic start.

### 4. Published inherited floor и original chronology остаются additive

Future v14 сохраняет original pre-mutation RED entry и existing saved tree,
independent Unicode 16.0.0 23-range/235-scalar oracle и exact digest bytes,
lexical depth-one direct connected scheduler activation, v11 runtime/task-root/
scheduler floor, exact 35-to-30 ownership, aggregate admission, four-stream
selection, full-only authority, source-safe four-step CI, connected
resolved-base guards и protocol-artifact non-authority.

Новая reproduction не заменяет original chronology. Terminal v13 forensic
payload не используется как source даже если он локально доступен.

### 5. Authorization не расширяет executable scope

Изменяются только card, same-slug artifacts, synchronized release-CI spec и
archive metadata. Future implementation зависит ровно от investigation v14,
integration decision, scheduler v1, authorization v13 и этой authorization;
блокирует только certification и добавляет максимум `499` production LOC.

## Risks / Trade-offs

- **[Risk]** Successor может частично повторить object в другом месте. →
  **Mitigation:** принимается только exact two-field published reference.
- **[Risk]** Usable executable может ошибочно пройти вместо declared token. →
  **Mitigation:** descriptor/source equality предшествует usability probes.
- **[Risk]** Data-only mutants могут имитировать guard coverage. →
  **Mitigation:** unique source/AST mutants и preceding-guard reachability
  обязательны.
- **[Risk]** Docs-only card может быть истолкована как affected authority. →
  **Mitigation:** она разрешает только создание separately reviewed successor;
  affected artifacts остаются non-authoritative.

## Migration Plan

1. Синхронизировать authorization requirements в main release-CI spec.
2. Архивировать same-slug change и получить fresh ordinary/high review.
3. Опубликовать card и remote branch.
4. Только после exact remote publication создать clean implementation v14 от
   authorization HEAD.

Rollback — не публиковать authorization; executable v14 state отсутствует.

## Open Questions

- Нет. Source, successor, ceiling, proof floor и dormancy определены точно.
