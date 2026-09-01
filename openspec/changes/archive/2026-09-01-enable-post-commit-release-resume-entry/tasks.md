## 1. Committed manifest proof

- [x] 1.1 Добавить RED cases в
  `scripts/smoke-delivery-manifest-derive.py` для exact
  `parent..payload`/manifest match, missing/extra/mismatched operations, wrong
  commit и commit без единственного parent; подтвердить, что existing helper
  не поддерживает требуемый committed proof.
- [x] 1.2 Расширить `bin/changerail-delivery-manifest scope-check` read-only
  target `committed` с обязательным `--commit`, переиспользовав текущую
  normalization add/modify/delete/rename без изменения manifest schema или
  working-tree/staged behavior.
- [x] 1.3 Обновить
  `skills/changerail-do/references/changerail-delivery-manifest.md` и довести
  focused committed-scope cases до GREEN.

## 2. State-specific lifecycle routing

- [x] 2.1 Добавить RED contract/negative-fixture coverage в
  `scripts/smoke-wiring-discovery.py`, которое отдельно извлекает normal и
  resume gate sets и падает, если normal утратил preflight/`--check-fresh`/
  working-tree/staged gates, resume вызывает их либо в resume отсутствуют
  schema/result/clean/parent/tree/committed/remote proofs.
- [x] 2.2 Обновить `skills/changerail-pub/SKILL.md`: объявить
  `--resume-release`, выбрать mode до общей Review Gate, сохранить initial
  pre-staging path и реализовать resume admission, exact release state machine,
  incompatible-flag rejection и hard stops из design/specs.
- [x] 2.3 Обновить `skills/changerail-deliver/SKILL.md`: объявить
  `--resume-release` и детерминированно направлять clean post-commit handoff
  прямо в matching publish route без `ff/do/review` и normal current-worktree
  gates.
- [x] 2.4 Довести wiring regression до GREEN и показать отдельные observed
  normal/resume sections/commands, включая safe interruptions после payload push,
  tag, release и partial upload, а также dirty/pre-commit, wrong lineage,
  scope, card, remote и asset negative cases без mutation.

## 3. Durable contract and linked-replacement handoff

- [x] 3.1 Согласовать `docs/release-discipline.md` с явным resume invocation,
  committed lineage/scope/remote admission, first-absent-step continuation и
  запретами force/replacement/extra review; не добавлять credentials,
  provider-specific substitution или machine-local evidence.
- [x] 3.2 Исправить только stale слова `повторного freshness/full-gate` в
  `openspec/changes/archive/2026-09-01-prepare-changerail-1-0-0-release/design.md`,
  сохранив predecessor history и exact release identity contract.
- [x] 3.3 Сверить implementation с обеими delta specs, выполнить
  `bin/openspec validate enable-post-commit-release-resume-entry --strict` и
  подготовить sync только нового change; два predecessor archived changes не
  переоткрывать и не дублировать.
- [x] 3.4 Вывести единый ignored successor delivery manifest, который включает
  весь сохраненный predecessor dirty release payload, linked replacement card,
  новый archive/synced specs и все skill/docs/helper/test paths; доказать
  working-tree scope parity до review handoff.

## 4. Successor final-certification floor

Cycle-1 outcomes ниже superseded: review доказал, что они относятся к
pre-archive tree. Rescue повторяет floor только после tracked freeze и хранит
новые exact-tree outcomes в ignored evidence/manifest без дальнейших tracked
edits.

- [x] 4.1 Заморозить один exact successor tree в isolated candidate с pinned
  `requirements-dev.txt` и CPU affinity `0,1`; все дальнейшие outcomes и
  fresh archive fingerprint связать только с этим tree в ignored evidence.
- [x] 4.2 Строго последовательно выполнить на candidate сначала
  `python3 scripts/run-release-baseline.py` с expected core `23/23`, затем
  `python3 scripts/run-release-baseline.py --suite extended` с expected
  extended `12/12`; не переносить и не дублировать inventory steps.
- [x] 4.3 Выполнить `python3 scripts/smoke-release-ci.py`,
  `python3 scripts/public-surface-scan.py` и
  `python3 scripts/public-surface-scan.py --history`; подтвердить exact
  release-CI inventory и нулевые findings current/history.
- [x] 4.4 Выполнить trusted npm SRI `4/4` и action tag `2/2` read-only checks из
  `docs/release-discipline.md`, не меняя pins, credentials или authority.
- [x] 4.5 Дважды построить source distribution из exact successor tree,
  подтвердить byte-identical assets, полный tracked archive layout,
  metadata/checksum и fresh SHA-256 в ignored evidence; predecessor checksum
  не переиспользовать как successor proof.
- [x] 4.6 Выполнить `python3 -m json.tool .mcp.json`, TOML parse
  `.codex/config.toml`, `bin/openspec validate --all --strict` и
  `git diff --check`; записать concise outcomes в successor manifest.
- [x] 4.7 Подготовить handoff на отдельную fresh-context xhigh final review для
  того же exact successor tree; не запускать publication и не считать
  predecessor `NO-GO` либо clean-HEAD audit новым `GO`.

## 5. Independent review cycle 1 rescue attempt 1

- [x] 5.1 Получить focused RED: section-aware routing отвергает missing late
  freshness; committed helper принимает replacement; distribution builder
  подменяет source bytes через replacement-aware view.
- [x] 5.2 После final verification перенести/rerun preflight, `--check-fresh`
  и working-tree scope непосредственно перед staging; staged scope оставить
  после staging и проверить same-path mutation fail-before-commit/push.
- [x] 5.3 Fail-closed отвергать `refs/replace/` и graft state, отключить
  replacement processing для commit/source reads и довести adversarial
  manifest/source fixtures до GREEN без mutation.
- [x] 5.4 Заменить marker-only trace oracle на реальные section/command order,
  forbidden cross-route gates, interruption handoffs и controlled wrong-state
  zero-mutation fixtures; focused wiring довести до GREEN.
- [x] 5.5 Подтвердить normalized preflight `ready-for-llm-review`, exact
  authorization, no new authority/wire и production LOC `397/400`; обновить
  tracked card/tasks до единственного freeze, после которого менять только
  ignored evidence/manifest для cycle-2 handoff.
