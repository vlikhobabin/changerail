## Context

Последняя безопасная опубликованная точка affected-profile lineage —
`authorize-bounded-affected-release-profile-v11` на exact commit
`9f72764e4969be9dcaebe08cabf06c6bbc9f4934`. Следующая docs-only попытка v12
осталась terminal unpublished: fresh cycle 1 дал `9/14` и три blocker, после
единственного same-card rescue cycle 2 дал `12/14`, два blocker и exhausted
budget `1/1/0`. Её tracked payload и raw runtime evidence не являются входом
этого решения.

Два незакрытых свойства относятся не к объёму production implementation, а к
независимости доказательства. Fragmented matching не доказывает, что raw RED
содержал требуемую exception line как один contiguous record. Oracle,
сформированный из production table или общего с ней промежуточного набора,
может подтвердить одинаковую ошибку в обеих сторонах.

## Goals / Non-Goals

**Goals:**

- задать exact line-equality oracle для retained missing-module RED;
- отделить Unicode oracle по ownership, представлению и происхождению данных от
  production table;
- сохранить exact Unicode 16.0.0 `Cc|Cf` inventory и закрытую direct activation
  форму;
- сохранить v11 runtime/scheduler и accumulated affected-profile floor;
- опубликовать только investigation/design contract перед отдельной v13
  authorization.

**Non-Goals:**

- читать, восстанавливать или исправлять terminal v12 payload/evidence;
- создавать authorization/implementation v13, focused tests, production или CI;
- запускать history, full/affected release, benchmark, live matrix или
  certification;
- давать affected mode publication authority.

## Decisions

### 1. Exact exception line является самостоятельным retained datum

Future v13 focused test обращается к реально отсутствующему
`changerail_release_affected_profile`. Captured raw output MUST содержать строку,
равную целиком:

```text
ModuleNotFoundError: No module named 'changerail_release_affected_profile'
```

Oracle сравнивает один элемент `splitlines()` по equality с полной literal
строкой и сохраняет эту строку в raw retained output. Два независимых
substring checks, regex из нескольких fragments, нормализованная/reconstructed
строка или поздний rerun не подходят. Это связывает конкретную failure cause с
тем же `status: failed`, non-zero exit, fingerprint и saved tree, которые были
получены до executable mutation.

Альтернатива — оставить fragment matching — отклонена: порядок, промежуточный
текст и даже разные exceptions могут удовлетворить два substring assertions.

### 2. Unicode oracle имеет независимый test-owned source dataset

Production представляет frozen Unicode 16.0.0 `Cc|Cf` inventory как 23
ordered non-overlapping ranges. Oracle MUST владеть отдельно написанным
test-only literal membership dataset в отличном представлении — полным набором
235 Unicode scalar values, полученным непосредственно из frozen Unicode 16.0.0
category source, а не из production ranges, production digest, production
iterator/helper или общего generated intermediate artifact.

Oracle не импортирует production constants для expected values и не вызывает
production normalization для построения expectation. Он самостоятельно:

1. строит membership predicate из test-owned scalar set;
2. вычисляет ожидаемые contiguous boundaries из этого set;
3. проверяет exact `23` ranges и `235` scalars;
4. сортирует ranges по ascending start; кодирует каждый endpoint ровно шестью
   uppercase ASCII hexadecimal digits, каждую range как `START-END`, соединяет
   records одним ASCII `;` без whitespace, BOM, newline или trailing delimiter;
   вычисляет SHA-256 этих ASCII/UTF-8 bytes и сравнивает с
   `7fb5126f7973cc51a27f62c8712c11401ace15b9d40afdf02f1575945dc1da81`;
5. отдельно проверяет, что U+11F00 отсутствует;
6. сравнивает production membership на members, boundary neighbors и stable
   nonmembers.

Review MUST видеть явное test-owned authoring/provenance note и отсутствие
пути данных от production table к expectation. Missing/extra scalar,
split/merged/reordered range, category drift или согласованная ошибка
production table+digest должны приводить к failure.

Альтернативы — импорт production table, копия тех же 23 ranges или generator,
который сначала читает production module — отклонены как self-certification.

### 3. Activation доказывается по lexical direct statement и public chain

В lexical `profile.main` MUST существовать ровно один direct statement, чьё
call-expression вызывает unaliased imported name `run_plan`. Вызов не может
быть вложен в `if` (включая constant `True/False`), conditional expression,
loop, `try`, `with`, nested function/lambda, wrapper, alias/attribute или другой
activation helper. Других `run_plan`/alternate activation calls в module нет.

Structural oracle проверяет AST shape, а connected oracle загружает actual
public runner → profile → scheduler chain и доказывает достижимость этого exact
call. Replacement production functions и disconnected fixture calls
запрещены.

### 4. V13 остаётся docs-only lineage stop

Эта карточка добавляет только свою card, same-slug artifacts, synchronized
release-CI spec и archive metadata. Следующий порядок фиксирован:

1. publish этой investigation;
2. отдельная docs-only `authorize-bounded-affected-release-profile-v13`;
3. clean `implement-bounded-affected-release-profile-v13` от authorization HEAD;
4. `certify-accelerated-release-loop-v1`.

Future authorization связывает exact successor и ceiling не выше 500; future
implementation использует только exact v13 authorization reference и добавляет
не более 499 production LOC. До authorization отсутствуют implementation card,
focused test и executable mutation.

## Risks / Trade-offs

- **[Risk]** Static 235-scalar fixture объёмнее range table. → **Mitigation:**
  Отличное представление и отдельное происхождение дают необходимую
  независимость; размер bounded и reviewable.
- **[Risk]** Runtime Python Unicode database может отличаться от 16.0.0. →
  **Mitigation:** oracle использует frozen test-owned dataset, а не ambient
  `unicodedata` как authority.
- **[Risk]** AST-only check может принять unreachable call. → **Mitigation:**
  structural lexical oracle дополняется connected execution через public chain.
- **[Risk]** Exact traceback formatting зависит от harness. → **Mitigation:**
  контракт требует equality одной raw output line, не полного traceback blob.

## Migration Plan

1. Синхронизировать этот decision в main release-CI spec и архивировать change.
2. Получить один fresh ordinary `gpt-5.6-sol/high` review и опубликовать.
3. Создать отдельную v13 authorization только от published investigation HEAD.
4. Не переносить файлы или raw evidence из terminal v12.

Rollback — не публиковать или отменить docs-only decision до создания
authorization; executable state отсутствует.

## Open Questions

- Нет. Exact line, independent dataset representation, frozen inventory,
  activation shape и дальнейший порядок закрыты этим решением.
