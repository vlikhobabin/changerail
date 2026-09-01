# Закрыть ambiguity cardinality в review-preflight authorization

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- none

## Series Index
- none

## Source
- Blocker R1 independent review cycle 1 карточки
  `authorize-bounded-post-commit-release-resume-entry-payload`: clean
  adversarial fixture с двумя полями `Investigation authorization` и лишней
  dependency authorization source прошел с exit `0`, authorization `valid` и
  outcome `ready-for-llm-review`.
- Published release-discipline decision требует fail-closed проверки обеих
  dependency edges перед semantic review exact successor.

## Summary
Сделать generic bounded-authorization boundary однозначным по cardinality:
parser должен рассматривать все exact authorization fields и relation sections,
принимать только один двухполевой successor reference, один шестиполевой source
object и точные reciprocal relations, а duplicated, extra или ambiguous формы
останавливать как `investigation-required` до semantic review. Исправление не
должно знать id конкретной release-card и не расширяет ее docs-only payload.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Blocks
- `authorize-bounded-post-commit-release-resume-entry-payload`

## Depends On
- `investigate-post-commit-release-resume-entry-boundary`

## Acceptance
- Generic parser/relation boundary не содержит special-case id release,
  authorization, investigation или successor card и остается существенно ниже
  обычного лимита 300 added production LOC.
- Non-default `Published investigation authorization` принимается только как
  ровно одно exact field в единственном `## Review` section и как JSON object с
  ровно двумя уникальными decoded keys `authorization_card` и
  `authorization_id`, оба значения — non-empty strings. Published source
  принимается только с одним exact `Investigation authorization` field в
  единственном `## Authorization` section и с ровно шестью уникальными decoded
  keys существующих типов; duplicate decoded keys, missing/extra keys и неверные
  types отклоняются fail closed.
- У каждой проверяемой relation есть ровно один одноименный section. В
  authorization source `## Depends On` содержит ровно одну нормализуемую card
  dependency и это exact investigation. В successor `## Depends On` и в
  investigation `## Blocks` exact required edge встречается ровно один раз;
  другие легитимные successor dependencies и другие targets shared
  investigation сохраняются совместимыми. Duplicate expected edge, duplicate
  section, missing/mismatched edge и extra authorization-source dependency
  отклоняются.
- Accepted relation forms остаются ограничены exact bare id, `<id>.md` и
  canonical `openspec/board/<lane>/<id>.md`; foreign stem, non-board path и
  ambiguous form не совпадают. Все 9 текущих published authorization sources и
  8 published successors остаются совместимыми с новым boundary.
- Invalid bounded chain возвращает exit `1`, authorization `status: invalid`,
  outcome `investigation-required` и `llm_review.required: false`; semantic
  review не получает eligibility.
- Focused adversarial matrix содержит как минимум exact positive chain,
  duplicate source field, duplicate successor reference, extra JSON key,
  duplicate/mismatched/extra authorization-source dependency и доказывает, что
  positive successor с unrelated dependencies и shared investigation с другими
  `Blocks` остаются допустимыми.
- Не ослабляются ceiling `301..500`, production LOC measurement, independent
  authority/protocol allowance, clean tracking-at-`HEAD`, path/id/status,
  `Blocks`/`Depends On`, scope, freshness, manifest, risk или public-surface
  gates.
- Изменяются только `scripts/changerail_review_preflight.py`, focused
  `scripts/smoke-review-preflight.py`, delta существующей capability
  `changerail-contracts` и минимальная соответствующая документация. Не
  меняются authorization/successor/release cards, их worktrees, release tag,
  `Release`/assets, schemas, providers, credentials, workflows или
  `.github/workflows/*`.

## Change Set
- `fix-review-preflight-exact-authorization-cardinality`

## Verify
- `taskset -c 0,1 python3 scripts/smoke-review-preflight.py`: RED на
  `duplicate successor reference`, затем GREEN `review preflight smoke: PASS`;
  rows вызывают production preflight и поэтому упадут при возврате invalid
  chain к `valid` либо semantic-review eligibility.
- `python3 -m py_compile scripts/changerail_review_preflight.py scripts/smoke-review-preflight.py`:
  PASS.
- `uvx --from ruff==0.6.9 ruff check scripts/changerail_review_preflight.py scripts/smoke-review-preflight.py`:
  PASS.
- `python3 scripts/smoke-contract-schemas.py`: PASS, 28 schemas.
- `bin/openspec validate fix-review-preflight-exact-authorization-cardinality --strict`:
  PASS before archive.
- `bin/openspec validate changerail-contracts --strict` и
  `bin/openspec validate --all --strict`: PASS before and after archive.
- `python3 scripts/public-surface-scan.py`: PASS, 1325 files, 0 findings.
- `PATH="$PWD/.runtime/changerail/ci-venv/bin:$PATH" taskset -c 0,1 python3 scripts/run-release-baseline.py`:
  PASS, 22/22 steps after installing pinned ignored-runtime dependencies.
- `git diff --check` и explicit `git diff --no-index --check` scan всех шести
  исходных untracked planning artifacts: PASS.

## Archive
- `openspec/changes/archive/2026-09-01-fix-review-preflight-exact-authorization-cardinality/`

## Related
- `scripts/changerail_review_preflight.py`
- `scripts/smoke-review-preflight.py`
- `docs/changerail-contracts.md`
- `openspec/specs/changerail-contracts/spec.md`
- `openspec/board/4.done/investigate-post-commit-release-resume-entry-boundary.md`
- `openspec/changes/archive/2026-09-01-fix-review-preflight-exact-authorization-cardinality/`

## Result
Generic exact-cardinality boundary, connected adversarial matrix, contract sync
и archive завершены. Payload ожидает один fresh independent ordinary `high`
review.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `fix-review-preflight-exact-authorization-cardinality`

### Why
First-match field extraction и presence-only relation matching допускают
ambiguous authorization source, хотя bounded authority должна быть единственной
и fail-closed до semantic review.

### Goal
Ввести минимальный generic exact-cardinality parser/relation boundary и
connected regression matrix без изменения существующей authorization schema,
authority или review routing.

### Scope
- Считать и валидировать все exact field/section occurrences на bounded
  authorization path, сохраняя unique-key JSON parsing и существующие type,
  path, status, tracking, ceiling и allowance checks.
- Сделать source dependency строгой single-edge relation; для successor и
  shared investigation требовать exact expected edge ровно один раз, но не
  запрещать unrelated relations.
- Добавить focused positive/negative fixtures и синхронизировать generic
  `changerail-contracts` wording с явным compatibility decision.
- Не менять конкретную authorization-card, successor, release-card или release
  publication surface.

### Acceptance
- Все card-level acceptance покрыты normative delta scenarios и tasks.
- Production implementation существенно меньше 300 added LOC и не добавляет
  authority, wire protocol, schema, provider, credential, workflow или mutation
  surface.

### Depends On
- `investigate-post-commit-release-resume-entry-boundary`

### Related
- `openspec/changes/fix-review-preflight-exact-authorization-cardinality/`

## Log
- 2026-09-01T12:14:09Z создана как отдельная planning-only prerequisite card
  по подтвержденному R1; production/tests, authorization payload, review,
  archive, commit и push в этой сессии запрещены.
- 2026-09-01T12:40:20Z test-first RED воспроизвёл fail-open duplicate
  successor reference; generic parser и connected adversarial matrix переведены
  в GREEN при 81 added production LOC.
- 2026-09-01T12:40:20Z focused checks, public scan и последовательный 22-step
  release baseline прошли; specs синхронизированы, change архивирован, card
  оставлена в `3.inprogress` для fresh independent ordinary review.
- 2026-09-01T13:08:39Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
