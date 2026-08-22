## Context

ChangeRail умеет связывать delivery с workspace/card/payload fingerprints, но
не имеет generic identity для внешней среды, на которой acceptance требует
получить доказательства. Project-specific commands могут вернуть green на
другой базе, сервисе или стенде, а runner и reviewer не отличат это от
объявленной цели. При этом ChangeRail не должен хранить endpoint, credentials,
содержимое среды или уметь создавать platform resources.

## Goals / Non-Goals

**Goals:**

- дать проекту optional tracked identity одной обязательной execution target;
- fail closed при отсутствии, drift, множественности или substitution evidence;
- перенести identity через plan/manifest, run status, blocker/resume и review;
- сохранить compatibility для проектов без declaration;
- удержать production-counted implementation не выше 500 строк.

**Non-Goals:**

- discovery, provision, clone, restore, registration или выбор среды;
- хранение network address, provider id, credential или target contents;
- проверка platform-specific fingerprint semantics generic core;
- dirty retained resume после intentional rebind.

## Decisions

### 1. Project-owned tracked declaration

Optional `.changerail/execution-target.json` имеет schema
`changerail.execution-target.v1` и ровно `schema`, `id`, `fingerprint`,
`target_substitution_policy`. `id` и fingerprint являются bounded
non-sensitive opaque strings; единственное policy value в v1 - `forbid`.
JSON выбран вместо добавления полей в несколько prose/config surfaces: он
однозначно schema-validatable, fingerprintable и не выполняет commands.

### 2. Одна canonical identity projection

Shared helper загружает declaration, отклоняет symlink/path escape, schema
errors и content-bearing extra fields и возвращает только logical id,
fingerprint и policy. Manifest, runner, review preflight и `verify-project`
переиспользуют эту projection; локальные альтернативные parsers запрещены.

### 3. Presence declaration делает target evidence обязательным

При отсутствии declaration текущий generic flow не меняется. При наличии
declaration planning manifest фиксирует identity, delivery status и evidence
ссылаются на exact projection, а review preflight требует ровно одну matching
target identity для применимых runtime checks. Missing, multiple или mismatched
identity fail closed. Physical endpoint и proof contents остаются во внешнем
project-owned oracle и ignored evidence.

### 4. Identity неизменна внутри attempt и recovery lineage

Single-card и plan runner сравнивают текущую declaration с captured identity
до child launch, перед review/publish и при resume. External blocker может
сохранить identity, но blocker/evidence не дают authority изменить ее.
Retained dirty resume требует exact match; target drift завершает path до child
launch.

### 5. Rebind только через новый clean attempt

Оператор меняет tracked declaration отдельным явным commit. После изменения
старые run/plan status, evidence, manifest и review verdict не могут быть
использованы для resume/publish. Новый delivery начинается из clean workspace
и создает новую lineage. ChangeRail не предоставляет `--target` override.

### 6. Bounded production boundary

Production-counted scope ограничен shared declaration helper, узким wiring в
`verify-project`, runner и review preflight. Schemas, templates, skills, docs и
smoke fixtures не входят в production count. Реализация MUST переиспользовать
существующие manifest/status fingerprint paths и остаться не выше 500 added
production-counted LOC; иначе authorization неприменима и требуется split.

## Risks / Trade-offs

- **Opaque fingerprint может быть сформирован неверно проектом.** ChangeRail
  проверяет consistency, а не domain truth; project-owned oracle отвечает за
  формирование и evidence.
- **Optional declaration не защищает legacy project автоматически.** Это
  сознательная compatibility boundary; target-required acceptance должна
  включить tracked declaration.
- **Дополнительные gates могут остановить старую recovery lineage после
  adoption.** Declaration adoption начинает новый clean attempt.
- **Scope может превысить LOC ceiling.** Shared parser/comparator и отсутствие
  provider integrations являются обязательной simplification boundary.
