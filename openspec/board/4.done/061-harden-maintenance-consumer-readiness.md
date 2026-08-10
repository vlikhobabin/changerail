# Довести maintenance harness до consumer-ready подключения

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Planning State
published; all card-owned OpenSpec changes implemented, independently reviewed,
synced to main specs, archived and finalized

## Series
- none

## Series Index
- none

## Source
- Post-delivery audit серии `060-repository-knowledge-maintenance` от
  2026-08-10.
- Воспроизведенный greenfield bootstrap через `bin/bootstrap-project
  --with-maintenance` и первый deterministic maintenance scan.

## Summary
Довести уже реализованный repository knowledge и maintenance harness до
полностью документированного и проверяемого consumer flow:

```text
install/adopt
  -> configure catalog and policy
  -> green initial index and scan
  -> audit and triage
  -> deduplicated card handoff
  -> scheduled read-only operation
  -> feedback normalization
  -> quality rollup
```

Текущие CLI, schemas, agent skills, bootstrap opt-in и scheduler examples
реализованы, но пользовательский путь фрагментирован между reference docs,
skills и examples. Свежий opted-in consumer проходит статический verifier, но
его initial maintenance scan не является зеленым без ручного исследования и
исправления стартового catalog/index.

## User Outcome
Оператор нового или существующего consumer repository может по одному
публичному runbook подключить maintenance harness, получить зеленый первый
deterministic scan, выбрать ручной или scheduled read-only режим, провести
bounded triage и получить quality output без чтения реализации, OpenSpec archive
или test fixtures.

## Observations And Evidence

### 1. Нет end-to-end maintenance runbook
- `README.md` показывает `--with-maintenance`, но не описывает полный первый
  запуск и последующий operational cycle.
- `docs/consumer-adoption-runbook.md` перечисляет opt-in helper wiring для
  существующего проекта, но не дает законченного catalog/policy/index/scan flow.
- `docs/changerail-contracts.md` содержит отдельные reference-секции для catalog,
  scan, lifecycle, baseline/cards и runner, но не заменяет operator runbook.

### 2. Feedback и quality отсутствуют в пользовательской документации
- `bin/changerail-maintenance feedback` принимает explicit review history,
  delivery run и external detector-result inputs.
- `bin/changerail-maintenance quality` строит text, JSON или CSV rollup из
  lifecycle reports, history, triage и proposal decisions.
- Поведение покрыто schemas, specs и smoke fixtures, но пользователь не получает
  documented input preparation, command examples, output interpretation или
  integration path.

### 3. Scheduler examples не обнаруживаются из основного documentation flow
- Public examples существуют под `examples/maintenance/` для Codex scheduled
  task, GitHub Actions, separated read/write CI и systemd.
- `README.md`, adoption docs и contracts не индексируют эти examples и не
  объясняют prerequisites consumer checkout/wiring.

### 4. Публичный contract reference отстает от реализованных schemas
- Schema inventory содержит
  `changerail.maintenance-quality-rollup.v1` и
  `changerail.maintenance-proposal-decision.v1`.
- В namespace/file inventory `docs/changerail-contracts.md` эти contracts не
  перечислены; отдельного feedback/quality reference нет.

### 5. Consumer verifier не покрывает два новых maintenance contracts
- `bin/verify-project` проверяет opted-in maintenance schemas только до
  `changerail-maintenance-run.schema.json`.
- Отсутствующие или stale quality-rollup/proposal-decision schemas поэтому не
  блокируют consumer verification.

### 6. Свежий maintenance bootstrap не дает зеленый initial scan
- Воспроизведенный `--with-maintenance` bootstrap прошел `verify-project`:
  `63/63` checks passed с отдельной unrelated auth-readiness diagnostic.
- `validate-catalog` прошел для двух generated catalog records.
- `render-index --check` завершился non-zero, потому что
  `.changerail/KNOWLEDGE.md` отсутствовал.
- `scan --json` вернул семь `major` findings: catalog coverage и orphan findings
  для `.changerail/knowledge.yaml`, `.changerail/maintenance.yaml` и
  `openspec/board/card-template.md`, а также missing generated index.
- Следовательно, opt-in создает wiring/config skeleton, но не подтверждает
  готовый first-run maintenance contract.

## Acceptance
- Добавлен public Russian end-to-end maintenance runbook для нового и
  существующего consumer repository: prerequisites, opt-in/adoption, catalog,
  policy, generated index, first scan, state, baseline/waiver boundary, audit,
  triage, cards, scheduler, feedback, quality и troubleshooting.
- `README.md`, documentation index и adoption runbook ведут к maintenance
  runbook; scheduler examples перечислены с назначением и безопасными
  prerequisites.
- Runbook содержит copy-pasteable generic POSIX commands и native Windows
  equivalents там, где surface поддерживается, используя только public-safe
  paths вроде `/opt/changerail` и `/opt/example-project`.
- Runbook явно отделяет read-only/default operations от explicit writes:
  `render-index --write`, `--write-state`, baseline write и card write; ни одна
  maintenance-команда не трактуется как разрешение на commit, push или publish.
- `feedback` документирован для review-cycle history, blocked delivery-run и
  external detector-result inputs, включая fail-closed validation и способ
  подключить normalized output через generic adapter boundary.
- `quality` документирован для text, JSON и CSV, complete/incomplete evidence,
  historical reports, triage/proposal inputs и семантики `known`/`unknown`.
- `docs/changerail-contracts.md` перечисляет все tracked maintenance schemas и
  содержит актуальные feedback, quality-rollup и proposal-decision contracts;
  устаревшая формулировка про future harness удалена.
- `verify-project` требует
  `changerail-maintenance-quality-rollup.schema.json` и
  `changerail-maintenance-proposal-decision.schema.json` для opted-in consumer и
  fail-closed обнаруживает отсутствующий или stale contract на POSIX и в
  generated-copy wiring where applicable.
- Fresh disposable consumer после `bootstrap-project --with-maintenance`
  проходит `validate-catalog`, `render-index --check` и `scan --json` без
  threshold-reaching findings и без ручного редактирования generated skeleton.
- Generated catalog/policy/index остаются deterministic, repository-relative и
  public-safe; повторный bootstrap/refresh не перезаписывает project-owned
  catalog customization без существующего ownership contract.
- Bootstrap без `--with-maintenance` не получает maintenance artifacts и
  продолжает проходить прежний verification baseline.
- Focused bootstrap/verify/repository-knowledge/runner smokes и полный release
  baseline покрывают исправленный consumer flow.

## Constraints And Non-goals
- Не включать deferred maintenance `fix` mode и не ослаблять negative entry gate
  карточки `060-06`.
- Не запускать full repository maintenance scan неявно внутри общего
  `verify-project`; verifier проверяет wiring/contracts, а отдельный focused smoke
  доказывает first-run scan behavior.
- Не превращать generic bootstrap catalog в исчерпывающую domain-specific
  knowledge taxonomy; стартовый skeleton должен быть зеленым и безопасно
  расширяемым consumer-ом.
- Не давать scheduled defaults commit, push, pull-request, issue-comment или
  external mutation authority.
- Не публиковать runtime reports, annotations, locks, raw logs, credentials или
  absolute consumer paths.
- Не поглощать широкий POSIX portability, profile, auth и CI bootstrap scope
  карточки `050-harden-greenfield-consumer-bootstrap`; здесь изменяется только
  maintenance-specific readiness.

## Triage Decisions
- Initial `.changerail/KNOWLEDGE.md` is a generated bootstrap artifact, not an
  implicit verifier or scan side effect. `bootstrap-project --with-maintenance`
  must create a deterministic, repository-relative index that already matches
  `render-index --check`; any later refresh must respect generated ownership and
  must not overwrite project-owned catalog or policy customization.
- `.changerail/knowledge.yaml` and `.changerail/maintenance.yaml` are part of
  the starter knowledge inventory and should be covered by active catalog
  records. Current `catalog-coverage` and `repository-orphans` inspect the
  configured `include_globs`; excluding `.changerail/**/*.yaml` would hide the
  opt-in contract from the first scan instead of documenting it.
- `openspec/board/card-template.md` gets a minimal `reference` catalog record
  owned by the consumer project, with `source_globs` pointing to itself and
  generic verification through `bin/verify-project .` and the maintenance
  catalog/index checks. This proves the starter board contract without imposing
  a broader consumer documentation taxonomy.
- Scheduler examples are public read-only integration templates. They are
  runnable only after a consumer checkout has maintenance config and helper
  wiring, or in the ChangeRail source checkout as dogfood examples; consumer CI
  documentation must say how the checkout reaches the ChangeRail source of truth
  and must not grant commit, push, comment, PR or external mutation authority.

## Change Set
- `make-maintenance-bootstrap-first-run-green`
- `complete-maintenance-consumer-verification`
- `publish-maintenance-operations-runbook`

## Verify
- `./bin/openspec list --json` -> `{"changes":[]}` after archive.
- `./bin/openspec validate --all --strict` -> `23` passed, `0` failed.
- `python3 scripts/smoke-bootstrap-project.py` -> pass `17/17`; latest report
  `.runtime/changerail/bootstrap-smoke/20260810T070059Z-24e4cc4f/report.json`.
- `python3 scripts/smoke-verify-project.py` -> pass `48/48`; latest report
  `.runtime/changerail/verify-project-smoke/20260810T065856Z-eb98dbe6/report.json`.
- `python3 scripts/smoke-repository-knowledge.py` ->
  `SMOKE_REPOSITORY_KNOWLEDGE_OK`.
- `python3 scripts/smoke-maintenance-runner.py` ->
  `SMOKE_MAINTENANCE_RUNNER_OK`.
- Fresh disposable `bin/bootstrap-project --with-maintenance` consumer passed
  `validate-catalog --json`, `render-index --check --json` and `scan --json`;
  scan emitted complete `changerail.maintenance-scan-report.v1` with zero
  findings/errors across starter detectors.
- `bin/changerail-python --check --json` reports required modules `tomllib`,
  `jsonschema` and `markdown_it`.
- `python3 scripts/smoke-python-runtime.py` -> pass `8/8`.
- `python3 scripts/smoke-windows-matrix.py` -> pass `6/7`, `0` failed, `1`
  not-run; live two-host smoke was not requested in local baseline.
- `python3 scripts/smoke-contract-schemas.py` ->
  `SMOKE_CONTRACT_SCHEMAS_OK (18 schemas)`.
- `python3 scripts/run-release-baseline.py` -> pass `31/31`.
- `python3 scripts/public-surface-scan.py` -> pass `889` files scanned,
  `0` findings.
- `python3 scripts/public-surface-scan.py --history` -> pass `889` files
  scanned, `0` findings.
- `git diff --check` -> passed.

## Archive
- `openspec/changes/archive/2026-08-10-make-maintenance-bootstrap-first-run-green/`
- `openspec/changes/archive/2026-08-10-complete-maintenance-consumer-verification/`
- `openspec/changes/archive/2026-08-10-publish-maintenance-operations-runbook/`

## Related
- `README.md`
- `docs/changerail-contracts.md`
- `docs/compatibility.md`
- `docs/consumer-adoption-runbook.md`
- `docs/maintenance-operations-runbook.md`
- `examples/maintenance/`
- `templates/project/.changerail/`
- `templates/project/README.md`
- `bin/bootstrap-project`
- `bin/changerail-python`
- `bin/verify-project`
- `bin/changerail-maintenance`
- `bin/changerail-maintenance-runner`
- `scripts/changerail_python_windows.py`
- `scripts/smoke-python-runtime.py`
- `skills/changerail-maintain/SKILL.md`
- `openspec/specs/changerail-project-bootstrap/spec.md`
- `openspec/specs/changerail-project-verification/spec.md`
- `openspec/specs/changerail-python-runtime/spec.md`
- `openspec/specs/changerail-repository-knowledge/spec.md`
- `openspec/board/1.backlog/050-harden-greenfield-consumer-bootstrap.md`
- `openspec/board/1.backlog/060-00-repository-knowledge-maintenance-program-epic.md`
- `openspec/board/1.backlog/060-06-add-scoped-maintenance-fix-mode.md`
- `openspec/board/4.done/060-05-connect-feedback-and-quality-rollup.md`

## Change 1: `make-maintenance-bootstrap-first-run-green`

### Why
Fresh opted-in consumers should not need to debug generated catalog/index state
before they can run the first deterministic maintenance audit.

### Goal
Make the `--with-maintenance` skeleton validate, have a current generated index
and scan below the configured threshold without manual edits.

### Scope
- Update maintenance bootstrap templates and bootstrap generation/refresh
  behavior for the initial catalog, policy and generated index.
- Add starter catalog records for `.changerail/knowledge.yaml`,
  `.changerail/maintenance.yaml` and `openspec/board/card-template.md`.
- Add focused disposable consumer regression coverage for first-run
  `validate-catalog`, `render-index --check` and `scan --json`.

### Acceptance
- Fresh `bin/bootstrap-project /opt/example-project --with-maintenance`
  produces `.changerail/knowledge.yaml`, `.changerail/maintenance.yaml` and a
  current `.changerail/KNOWLEDGE.md`.
- In that fresh consumer, `./bin/changerail-maintenance validate-catalog --json`,
  `./bin/changerail-maintenance render-index --check` and
  `./bin/changerail-maintenance scan --json` all complete without
  threshold-reaching findings.
- Bootstrap without `--with-maintenance` still creates no maintenance artifacts.
- Repeat bootstrap/refresh does not overwrite project-owned catalog or policy
  customization and only updates generated-owned artifacts under an explicit
  ownership contract.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-08-10-make-maintenance-bootstrap-first-run-green/`

## Change 2: `complete-maintenance-consumer-verification`

### Why
Opted-in consumers currently pass verification even if the latest maintenance
quality/proposal contracts are missing from the reachable schema inventory.

### Goal
Make `verify-project` fail closed on incomplete maintenance contract wiring for
both normal POSIX and generated-copy consumer setups, without running a full
maintenance scan inside the general verifier.

### Scope
- Add `changerail-maintenance-quality-rollup.schema.json` and
  `changerail-maintenance-proposal-decision.schema.json` to the opted-in
  maintenance schema inventory.
- Update verify smoke fixtures for complete, missing and stale maintenance
  contract surfaces.
- Preserve the current opt-out behavior for consumers with no maintenance
  artifacts.

### Acceptance
- `bin/verify-project` reports both quality/proposal schema files as required
  for opted-in maintenance consumers.
- Missing or stale required maintenance schema/helper wiring fails closed in
  focused POSIX and generated-copy fixtures where the wiring backend owns those
  artifacts.
- `verify-project` still does not execute `bin/changerail-maintenance scan` as
  part of the generic project verification path.

### Depends On
- `make-maintenance-bootstrap-first-run-green`

### Related
- `openspec/changes/archive/2026-08-10-complete-maintenance-consumer-verification/`

## Change 3: `publish-maintenance-operations-runbook`

### Why
The implemented maintenance harness is discoverable only by reading reference
docs, skills, examples and fixtures; consumers need one operator runbook.

### Goal
Publish the end-to-end consumer runbook and update reference docs/indexes so an
operator can adopt, run, schedule, triage, normalize feedback and read quality
rollups without reading implementation internals.

### Scope
- Add a public Russian maintenance operations runbook for new and existing
  consumers.
- Link it from `README.md`, documentation index/adoption docs and relevant
  contract references.
- Document scheduler examples, feedback normalization and quality rollup
  commands with safe POSIX and native Windows examples where supported.

### Acceptance
- The runbook covers install/adopt, catalog/policy/index, first scan, state,
  baseline/waiver boundary, audit, triage, deduplicated cards, scheduled
  read-only operation, feedback, quality and troubleshooting.
- Read-only/default commands are separated from explicit writes:
  `render-index --write`, `--write-state`, baseline write and card write.
- `docs/changerail-contracts.md` lists every tracked maintenance schema,
  including quality rollup and proposal decision, and contains current feedback
  and quality reference sections instead of stale future-harness wording.
- Scheduler examples are indexed with their prerequisites and least-privilege
  limits; none of the examples implies commit, push, PR, comment or external
  mutation authority.

### Depends On
- `make-maintenance-bootstrap-first-run-green`
- `complete-maintenance-consumer-verification`

### Related
- `openspec/changes/archive/2026-08-10-publish-maintenance-operations-runbook/`

## Result
delivery, archive, independent review and scoped publish finalization complete.
Exact payload and published commit ledger is retained in the ignored delivery
manifest.

## Next
- done

## Log
- `2026-08-10` — card создана по итогам post-delivery documentation и
  greenfield maintenance bootstrap audit.
- `2026-08-10T05:56:14Z` — triage decisions resolved from code/templates/docs
  and disposable bootstrap reproduction; owner assigned, ordered change plan
  recorded, and card moved to `2.todo` as deliver-ready.
- `2026-08-10T06:22:08Z` — internal `ff` phase created apply-ready OpenSpec
  artifacts for all three card-owned changes; strict validation passed and card
  moved to `3.inprogress` for delivery.
- `2026-08-10T07:03:22Z` — all three OpenSpec changes implemented, verified and
  archived; release baseline passed `31/31`. During baseline, runtime readiness
  was aligned with existing `requirements-runtime.txt` so maintenance Markdown
  link checks fail early when `markdown_it` is missing.
- 2026-08-10T07:21:50Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
