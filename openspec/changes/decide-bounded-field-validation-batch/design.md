## Context

Deterministic preflight останавливает payload выше 300 production LOC, новый
authority/wire protocol и любой unresolved repeated defect. Published
authorization может поднять exact successor ceiling только до 500 и разрешить
только explicitly investigated protocol boundary. Поэтому один общий waiver
или prose assertion недостаточны.

## Goals / Non-Goals

**Goals:**

- принять отдельное bounded решение для каждого из шести successors;
- сделать решения consumable exact authorization sources;
- ограничить duplicate production paths через shared helpers;
- закрыть repeated-defect uncertainty без дополнительного rescue budget.

**Non-Goals:**

- реализация successors;
- создание authorization source в этом change;
- повышение default/global ceiling;
- разрешение credential, provider или substitution authority.

## Decisions

### 1. Одна investigation, отдельные authorizations

Одна investigation допустима, потому что она перечисляет все exact successors
в `Blocks` и содержит отдельное решение для каждого. Каждый successor все равно
получит собственный `4.done` authorization source с одним exact JSON object;
authorization нельзя переиспользовать между cards.

### 2. Ceiling 500 является hard maximum, не target size

Каждая реализация должна минимизировать production delta и MAY быть меньше
300. `500` лишь upper bound. Если exact payload выше 500, delivery не меняет
authorization, а создает split/replacement investigation.

### 3. Shared-helper boundaries обязательны

Target declaration, retained recovery, verification map и source profile
имеют по одному canonical loader/comparator. Progress и episode lineage имеют
по одному runner-owned owner record. Это устраняет наиболее вероятный источник
duplicate production LOC и inconsistent validation.

### 4. Repeated symptom не переносится как бесконечный rescue

Для target substitution, external recovery, verification coverage и source
profiles investigation выбирает одну testable hypothesis и exact scope.
Successor после publication может иметь `Repeated defect class: no`, потому что
он реализует investigated decision, но повтор того же blocker не разрешает
same-card extension: требуется новая investigation/split.

## Risks / Trade-offs

- **Один successor все равно может превысить 500.** Review preflight остается
  fail closed; решение явно требует split.
- **Общая investigation может скрыть card-specific nuance.** Decision и
  verification floor перечислены отдельно для каждого id/path.
- **Флаг repeated меняется после investigation.** Card log и dependency
  сохраняют происхождение и запрещают трактовать это как новый rescue budget.
