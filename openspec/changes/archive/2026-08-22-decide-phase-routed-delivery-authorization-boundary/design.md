## Context

Исходная карточка `add-phase-routed-delivery-plan-execution`
исчерпала два same-card rescue attempts. Fresh cycle-3 review на
payload fingerprint
`sha256:93b354321da8e60e85508c622c96f6c477e2f5fba383efd30dc684b002694cbe`
подтвердил, что основной monolithic path не изменен, но нашел
пять blockers и один major test gap на новой aggregate/child
dirty-worktree authorization boundary:

- schema разрешает отсутствующий `max_repair_cycles`, aggregate
  считает его равным 1, а child authorization — 0;
- `resume-plan` проверяет новый child по previous aggregate status
  до материализации parent для нового run;
- authorization ошибочно требует `card.id == filename stem`, хотя
  schema разрешает alias id;
- plan CLI принимает alternate aggregate `--runtime-root`, но child
  authorization ищет parent только в default root;
- протокол дает новую authority для dirty worktree, но исходная
  карточка не объявила new authority/wire protocol и не имеет
  published authorization;
- aggregate sequencing/resume smoke заменяет production child фейком
  и поэтому не наблюдает эту boundary.

Неопубликованный payload содержит 299 added production-counted
LOC в runner и остается investigation input, а не разрешенной к
публикации реализацией. Этот change публикует только
решение; production поведение принадлежит будущему exact
replacement.

## Goals / Non-Goals

**Goals:**

- Выбрать один contract для repair budget, card identity, resume и
  aggregate runtime root.
- Определить минимальную parent/child authority boundary и
  fail-closed tampering cases.
- Привязать каждый cycle-3 finding к production regression probe.
- Назвать exact replacement, exact authorization source и bounded LOC
  ceiling.

**Non-Goals:**

- Не изменять `bin/changerail-delivery-runner`, schemas, smoke tests,
  CLI, docs или runtime behavior в этой карточке.
- Не публиковать и не чинить cycle-3 payload исходной карточки.
- Не давать broad waiver для других runner protocols и не повышать
  global complexity ceiling.
- Не обещать защиту от злонамеренного пользователя, который
  может согласованно переписать все ignored runtime records и
  tracked plan; для такой trust boundary нужен отдельный signed или
  privileged authority design.

## Decisions

1. **Repair budget является обязательным explicit полем.** Когда plan
   включает phase routing, `max_repair_cycles` MUST быть целым
   числом в допущенном schema range; 0 явно запрещает repair.
   Отсутствующее поле делает plan invalid до aggregate status, lock,
   preflight и child launch. Aggregate transition и child authorization читают
   только это explicit value и не имеют локальных defaults.

   Rejected: default 1 неявно выдает repair authority. Rejected: default 0
   молча отключает advertised repair route. Required field делает
   operator intent одинаково observable в schema, aggregate и child.

2. **Canonical card lookup и declared id — разные части identity.** Parent
   card однозначно выбирается по `(workspace alias, canonical
   resolved card path)`. Workspace alias MUST однозначно разрешаться в
   canonical workspace root, а plan semantics MUST отклонять duplicate
   resolved card paths. После lookup parent entry's declared `card.id`
   сохраняется как authoritative plan identity и входит в expected
   child run/status identity. Он не выводится из filename stem.

   Rejected: lookup только по declared id не доказывает, что child
   получил нужный card path. Rejected: `card.id == filename stem`
   ломает schema-valid aliases и existing queue contract.

3. **Resume сначала материализует новую authority.** `resume-plan`
   MUST выполнить такую последовательность до dirty child preflight:

   1. Загрузить previous canonical aggregate status и связанный
      terminal child status; оба должны пройти schema и identity
      checks.
   2. Доказать exact resumable transition, неизменные plan и payload
      fingerprints и точную card/workspace identity.
   3. Выделить новый aggregate run id, увеличить phase attempt
      и вывести expected child run id/status path из нового aggregate,
      declared card id, phase и attempt.
   4. Атомарно записать schema-valid new parent status в
      canonical aggregate root с `phase: resuming`, `result: RUNNING` и
      `resume_from`, привязывающим previous aggregate run id, canonical
      status path и fingerprint previous status.
   5. Передать только этот new parent в production single-card
      preflight. Lock и child launch остаются после успешного
      preflight.

   Rejected: передавать previous parent с новым child id. Его
   identity по определению не может авторизовать child другого
   aggregate run.

4. **Возобновляем только exact same-phase `BLOCKED` receipt.**
   Допустимый transition:

   ```text
   phase=P, attempt=N, result=BLOCKED
     -> phase=P, attempt=N+1, result=RUNNING
   ```

   Previous receipt и его child status MUST совпадать по phase,
   attempt, run id, status path, terminal `BLOCKED`, card/workspace и payload
   fingerprint. Plan fingerprint, repair count и active payload MUST остаться
   неизменными. New attempt не удаляет previous receipt и не
   переиспользует previous child run id.

   Terminal `DELIVERED`, review `GO`, exhausted-budget `NO-GO`, invalid или
   missing child status, pre-child aggregate failure без matching `BLOCKED`
   receipt, plan drift и payload drift не возобновляются через эту
   authority. Это не позволяет превратить один blocked receipt в
   reusable dirty-tree bypass.

5. **Phase routing использует только canonical aggregate runtime
   root.** Canonical parent path:
   `<consumer-root>/.runtime/changerail/delivery-plans/<aggregate-run-id>/status.json`.
   Если explicit `--runtime-root` после normalization отличается от
   этого root, phase-plan admission MUST завершиться `BLOCKED` до
   child preflight/lock/launch. CLI и docs MUST явно сказать, что override
   остается для monolithic plan mode, но не поддерживается phase
   routing.

   Rejected: добавить runtime-root identity в parent/child wire. Это
   расширяет authority, path normalization и tampering surface без
   доказанной operator need для opt-in mode.

6. **Parent status является fail-closed operational authority, но не
   cryptographic trust anchor.** Минимальный authority set для dirty child
   состоит из:

   - plan id, canonical path и fingerprint;
   - aggregate run id и canonical parent status path;
   - workspace alias и canonical root;
   - declared card id, declared/canonical card path;
   - active phase и phase attempt;
   - expected child run id и canonical child status path;
   - current payload `head_commit`, `tree_sha` и `diff_fingerprint`;
   - для repair — explicit budget, used count и matching review `NO-GO`
     receipts;
   - для resume — previous aggregate identity/status fingerprint и exact
     last `BLOCKED` receipt.

   Timestamps, display reasons, summaries, checks, progress, locks, давняя history
   кроме required predecessor и model/effort receipts являются
   provenance/observability, а не отдельной dirty-tree authority. Effective
   child route MUST выводиться из повторно валидированного tracked
   plan, а не из свободно редактируемого provenance.

   Schema failure, noncanonical/relocated parent, duplicate or ambiguous
   card/workspace entry, одиночное изменение любого authority
   поля, plan/payload drift, stale run, wrong transition или broken resume
   lineage MUST завершать preflight fail closed. Полностью
   согласованную same-user подмену plan, payload и всех runtime
   records без внешнего trust anchor обнаружить нельзя; это
   явная граница модели, а не предлог ослабить consistency checks.

7. **Один exact replacement получает bounded authorization.** Exact
   successor id: `implement-phase-routed-delivery-authorization-boundary`.
   Initial path:
   `openspec/board/2.todo/implement-phase-routed-delivery-authorization-boundary.md`;
   authorization-time path:
   `openspec/board/3.inprogress/implement-phase-routed-delivery-authorization-boundary.md`.
   Exact authorization source id:
   `authorize-bounded-phase-routed-delivery-payload`, initial path
   `openspec/board/2.todo/authorize-bounded-phase-routed-delivery-payload.md`
   и published path
   `openspec/board/4.done/authorize-bounded-phase-routed-delivery-payload.md`.

   Authorization object MUST связать published investigation, exact
   successor id/path, production LOC ceiling 500 и
   `allow_new_authority_or_wire_protocol: true`. Одна replacement-карточка
   предпочтительна: 299-line investigation input и bounded fixes
   помещаются в допустимый 301..500 exception, а schema, aggregate
   writer и child validator должны публиковаться атомарно. Разделение,
   которое временно делает writer и validator несовместимыми,
   отвергнуто. Если successor не укладывается в 500, он
   MUST остановиться для нового investigation/split decision, а не
   ослаблять проверки и не повышать ceiling.

8. **Regression matrix использует production authorization
   boundary.** Successor MUST покрыть:

   | Finding | Production probe | Expected result |
   | --- | --- | --- |
   | R1 | Explicit budget 0/1 через aggregate-to-child; omitted budget через production plan admission | Explicit values одинаковы в aggregate/child; omission отклонен до child |
   | R2 | Real phase child пишет `BLOCKED`, `resume-plan` создает new aggregate/child ids | New canonical parent существует до production preflight; exact same-phase retry passes |
   | R3 | Plan id alias отличается от filename stem | Unique workspace/path lookup и declared-id child binding pass |
   | R4 | Default root и alternate `--runtime-root` | Default passes; alternate phase plan is rejected before child |
   | R5 | Deterministic review preflight для exact successor | Published investigation/authorization chain и protocol declaration pass; any mismatch is `investigation-required` |
   | R6 | Aggregate start/transition/resume вызывают production single-card preflight | Fake child не является evidence для authority claims |

   Negative probes MUST по одному и в комбинации изменять plan
   id/path/fingerprint, aggregate run/path, workspace alias/root, declared card
   id/path, phase, attempt, child run/status path, payload fingerprint, repair
   count/budget, last receipt и resume lineage. Duplicate card/path entries,
   relocated parent, stale previous status, reused child id, terminal `NO-GO`/`GO`
   resume и payload drift MUST fail before child launch. Fake child может
   остаться только в tests, которые проверяют агрегатный
   scheduling/presentation и не заявляют authority coverage.

## Risks / Trade-offs

- [Risk] Required budget breaks schema-valid phase plans built against the
  unpublished payload. → Mitigation: payload не опубликован; explicit migration
  error появится до runtime mutation.
- [Risk] Canonical-only runtime root reduces phase-mode operator flexibility.
  → Mitigation: monolithic mode сохраняет override, а ранний diagnostic
  заменяет поздний необъяснимый child failure.
- [Risk] A new preflight parent could look like erased history. → Mitigation:
  required `resume_from` binding и immutable previous receipt сохраняют
  lineage; previous status не переписывается.
- [Risk] Same-user runtime files can be forged coherently. → Mitigation: state
  this trust limit explicitly, validate every independently derivable field and
  keep signature/privileged-writer design outside this bounded successor.
- [Risk] 500 LOC pressure could weaken tests. → Mitigation: regression matrix
  is mandatory and over-ceiling work stops for a new split decision.

## Migration Plan

1. Publish this decision-only investigation and archive its OpenSpec change.
2. Create and publish
   `authorize-bounded-phase-routed-delivery-payload` with exactly one
   authorization object for this investigation, the exact successor, ceiling
   500 and protocol allowance `true`.
3. Create `implement-phase-routed-delivery-authorization-boundary` as a new
   replacement card; do not reopen a third repair of
   `add-phase-routed-delivery-plan-execution`.
4. Rebuild the bounded payload from the rejected implementation input, apply
   every selected contract atomically and run the complete production matrix.
5. Require fresh independent `GO` before publish or any two-card pilot wave.

Rollback is documentation-only for this change: revert the unpublished
decision artifacts. No production or runtime migration occurs here.

## Open Questions

- none
