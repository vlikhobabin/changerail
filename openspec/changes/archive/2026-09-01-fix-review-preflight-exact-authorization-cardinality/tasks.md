## 1. Connected Regression Matrix

- [x] 1.1 Расширить generic canonical fixture в
  `scripts/smoke-review-preflight.py`: exact chain MUST проходить с unrelated
  successor dependency и дополнительным target shared investigation, сохраняя
  `valid`/`ready-for-llm-review`.
- [x] 1.2 Добавить RED table rows для duplicate successor
  `Published investigation authorization`, duplicate source
  `Investigation authorization`, duplicate section и duplicate/extra decoded
  JSON keys; каждый row MUST проверять exit `1`, `invalid`,
  `investigation-required` и `llm_review.required: false`.
- [x] 1.3 Добавить RED source-relation rows для missing, duplicate, mismatched и
  extra `Depends On`, а также duplicate expected edge/section successor и
  investigation; сохранить existing bare id, filename и canonical board-path
  positives.

## 2. Exact-Cardinality Boundary

- [x] 2.1 В `scripts/changerail_review_preflight.py` заменить first-match
  authorization extraction на bounded enumerator exact sections/fields,
  который сохраняет legacy absent/single-`none`, но отклоняет duplicate
  non-default declaration и ambiguous section cardinality.
- [x] 2.2 Добавить pair-preserving или эквивалентный exact-object decoder для
  two-field reference и six-field source: duplicate decoded keys, missing/extra
  keys, non-object/trailing input и неверные types MUST давать structured
  `invalid` до path/relation semantics.
- [x] 2.3 Разделить relation checks: source `Depends On` MUST быть exact
  single-item/single-reference dependency, а successor `Depends On` и
  investigation `Blocks` MUST содержать required edge ровно один раз в
  единственном section, сохраняя unrelated relations.
- [x] 2.4 Сохранить без ослабления ceiling `301..500`, LOC measurement,
  protocol allowance, repeated-defect, clean tracking-at-`HEAD`,
  path/id/status, scope/freshness/risk gates и существующий ordering
  `invalid -> investigation-required -> no semantic review`; подтвердить не
  более 150 added production LOC и отсутствие card-specific ids.

## 3. Contract And Documentation

- [x] 3.1 Обновить только bounded-authorization paragraph в
  `docs/changerail-contracts.md`: exact field/JSON/relation cardinality,
  source-only strict dependency и совместимость unrelated successor/
  investigation relations.
- [x] 3.2 Синхронизировать delta `changerail-contracts` во время apply и явно
  зафиксировать, что active exact-one published source contract supersedes
  прежнюю multi-candidate tolerance для нескольких exact source fields, не
  затрагивая JSON вне field или текущие 9 source/8 successor patterns.
- [x] 3.3 Проверить scoped paths: authorization/successor/release cards и их
  worktrees, release tag/`Release`/assets, schemas, providers, credentials,
  workflows и `.github/workflows/*` MUST отсутствовать в implementation diff.

## 4. Verification And Handoff

- [x] 4.1 Запустить `python3 scripts/smoke-review-preflight.py`; подтвердить,
  что каждый adversarial row падает на production boundary, а exact positive
  chain и прежние legitimate authorization patterns проходят.
- [x] 4.2 Запустить
  `python3 -m py_compile scripts/changerail_review_preflight.py scripts/smoke-review-preflight.py`,
  `ruff check scripts/changerail_review_preflight.py scripts/smoke-review-preflight.py`
  и `python3 scripts/smoke-contract-schemas.py`.
- [x] 4.3 Запустить `bin/openspec validate
  "fix-review-preflight-exact-authorization-cardinality" --strict`, после sync
  `bin/openspec validate "changerail-contracts" --strict` и
  `bin/openspec validate --all --strict`.
- [x] 4.4 Запустить `python3 scripts/public-surface-scan.py`,
  `python3 scripts/run-release-baseline.py`, `git diff --check` и explicit
  whitespace scan всех новых untracked artifacts.
- [x] 4.5 Синхронизировать specs, архивировать change и оставить card в
  `3.inprogress` для fresh independent ordinary review; не применять,
  review-ить или публиковать blocked authorization-card в этом payload.
