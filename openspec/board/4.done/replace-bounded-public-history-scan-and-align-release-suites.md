# Заменить bounded public history scan и согласовать release suites

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
- Exhausted source id: `implement-bounded-public-history-scan-runtime`
- Safe published base: `16d441e8b5f4d8a415ae011e46cce5b3863a1010`
- Source fingerprint:
  `sha256:572256168a43edd2f97c26eca3f22be68473ff4007726c71624d364d63c467c7`
- Linked replacement after review cycles `1..3`, rescue attempts `0..2` and
  exhausted same-card budget `2/2`.

## Summary
Заново реализовать от safe published base весь coherent publish unit: bounded
`HEAD` unique-blob history scanner с focused fixture, Linux-focused default
core, отдельную scheduled/manual extended suite, exact disjoint inventories,
full-history CI checkout, public docs и согласованные `release-ci` /
`release-discipline` contracts.

Source acceptance прошла `6/6`, но overall verdict остался `NO-GO`, потому что
финальный normative contract всё ещё назначал one-command delivery regression
default core. Fixed product decision: regression принадлежит только extended,
а exact normative invocation —
`python3 scripts/run-release-baseline.py --suite extended`.

## Review
- Risk tier: `ordinary`
- Review effort: `high`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

Весь coherent payload ограничен `<=300` added production LOC. Новая authority,
dependency, release-ref CLI или wire/report schema запрещены. Fresh manifest,
evidence и independent review обязательны после реализации.

## Lineage
- Blocker classes: raw mode/framing oracle; timeout/non-zero oracle; suite
  inventory/non-overlap; full checkout `fetch-depth: 0`; final normative
  ownership mismatch.
- Source dirty payload является только неавторитетной справкой. Его unpublished
  card/archives, runtime state, raw logs, manifest, evidence и verdict не входят
  в replacement scope и не переносятся.
- Published decision source остаётся
  `openspec/changes/archive/2026-08-31-decide-bounded-public-history-scan-runtime/`.

## Depends On
- `decide-bounded-public-history-scan-runtime`

## Blocks
- `stabilize-first-stable-release-scope`
- `prepare-1-0-0-stable-release`

## Acceptance
- `--history` разрешает один полный `HEAD^{commit}`, игнорирует unrelated refs,
  сканирует каждый unique public blob один раз и сохраняет complete structured
  commit/path attribution максимум за три Git process launches.
- Focused public-safe fixture минимум с 250 commits/20 paths доказывает
  semantic parity, valid raw mode transitions, strict raw/batch framing,
  timeout/non-zero/EOF/pipe failures, redacted non-zero outcome и завершение
  под `timeout 30s`.
- Default `python3 scripts/run-release-baseline.py` является Linux-focused core
  и проходит в clean checkout под `timeout 300s`; оба release workflow используют
  pinned checkout с `fetch-depth: 0`.
- Runner и CI oracle публикуют exact ordered 22-item core и 12-item extended
  inventories, отклоняют missing/extra/duplicate/overlap и не включают Windows
  diagnostics ни в одну suite.
- `python3 scripts/smoke-delivery-runner.py` принадлежит только extended;
  default core его не выполняет, а release procedure требует exact invocation
  `python3 scripts/run-release-baseline.py --suite extended`.
- `changerail-release-ci`, `changerail-release-discipline`, release docs и
  compatibility caveat согласованы с Linux-focused claim, отдельным extended
  route и retained opt-in Windows diagnostics.
- Весь replacement остаётся в `<=300` added production LOC без новой authority
  или protocol; дальнейшие manifest/evidence/review создаются fresh и scoped
  только к этому payload.

## Change Set
- `replace-bounded-public-history-scan-and-align-release-suites`

## Verify
- `python3 scripts/public-surface-scan.py --self-test`
- `timeout 30s python3 scripts/smoke-public-surface-history.py`
- `python3 scripts/smoke-release-ci.py`
- `python3 scripts/smoke-verify-project-sharding.py`
- `timeout 300s python3 scripts/run-release-baseline.py`
- `python3 scripts/run-release-baseline.py --suite extended`
- `python3 scripts/smoke-windows-entrypoints.py`
- `python3 scripts/smoke-windows-wiring-git-safety.py`
- `bin/openspec validate
  replace-bounded-public-history-scan-and-align-release-suites --strict`
- `bin/openspec validate --all --strict`
- `python3 scripts/public-surface-scan.py`
- `python3 scripts/public-surface-scan.py --history`
- `git diff --check` with untracked files included by a safe method

## Archive
- `openspec/changes/archive/2026-08-31-replace-bounded-public-history-scan-and-align-release-suites/`

## Related
- `openspec/board/4.done/investigate-bounded-public-history-scan-runtime.md`
- `openspec/changes/archive/2026-08-31-decide-bounded-public-history-scan-runtime/`
- `openspec/changes/archive/2026-08-31-replace-bounded-public-history-scan-and-align-release-suites/`
- `scripts/public-surface-scan.py`
- `scripts/run-release-baseline.py`
- `docs/release-discipline.md`

## Result
Implementation, verification, spec sync и archive завершены при 272 added
production LOC. Operator-authorized remediation разделил обязательный
`scripts/smoke-verify-project.py` ровно на два bounded worker-а `39 + 30` без
потери 69 scenarios; отдельный process oracle проверяет parity/order,
single-failure propagation, exception, crash, timeout, missing, duplicate,
malformed result, isolation и cleanup.

Fresh-checkout core завершился `22/22` за `198.548s`; final post-archive
`timeout 300s python3 scripts/run-release-baseline.py` завершился `22/22` за
`206.012s`, включая `69/69` verify-project и current/history public scans
`1305 files, 0 findings`. Exact extended suite завершилась `12/12` за
`225.467s`; opt-in Windows diagnostics завершились `67/67` и `6/6`. Strict
OpenSpec, config parsing, source classification и whitespace gates GREEN.
Retained evidence:
`.runtime/changerail/evidence/replace-bounded-public-history-scan-and-align-release-suites/index.json`.
Normalized deterministic preflight: `ready-for-llm-review`, ordinary/high,
complexity `272/300`, exact working-tree scope; path:
`.runtime/changerail/review-preflights/replace-bounded-public-history-scan-and-align-release-suites.json`.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `replace-bounded-public-history-scan-and-align-release-suites`

### Why
После исчерпания source review budget технически зелёный payload нельзя
публиковать: suite ownership в normative release discipline не совпадает с
runner/CI split.

### Goal
Построить clean coherent replacement от safe base, который одновременно
реализует bounded scanner и делает code, exact suite inventories, workflows,
docs и оба normative contracts непротиворечивыми.

### Scope
- bounded `HEAD` unique-blob scanner и focused public-safe fixture;
- source classification, local runner, default/extended CI и exact CI oracle;
- operator-authorized bounded `scripts/smoke-verify-project.py` sharding и
  focused `scripts/smoke-verify-project-sharding.py` process oracle;
- Linux-focused release/compatibility docs;
- `changerail-release-ci` и `changerail-release-discipline` delta specs;
- fresh delivery evidence/manifest и последующий independent high-effort review;
- не более 300 added production LOC, без новой authority/protocol.

### Acceptance
- Все story acceptance criteria доказаны fresh checks; one-command delivery
  regression находится только в extended и запускается exact normative command.

### Depends On
- `decide-bounded-public-history-scan-runtime`

### Related
- `openspec/changes/archive/2026-08-31-replace-bounded-public-history-scan-and-align-release-suites/`

## Log
- 2026-08-31 linked replacement создан от safe published base после exhaustion
  source review budget; old unpublished payload не включён в scope.
- 2026-08-31 proposal, design, release-ci/release-discipline delta specs и tasks
  подготовлены для standalone `changerail-do` handoff.
- 2026-08-31 fresh implementation completed at 272 added production LOC;
  focused scanner and exact inventory gates passed, but two exact core attempts
  and an isolated mandatory smoke diagnostic confirmed the 300-second timeout,
  so delivery stopped before spec sync/archive/review handoff.
- 2026-08-31 operator-authorized blocker remediation сохранил exact 69-scenario
  behavior в двух shard-worker-ах `39 + 30`; SHA-256-matched fresh core прошёл
  `22/22` за `198.548s`.
- 2026-08-31 required extended suite, opt-in diagnostics, strict/public/config
  gates и focused sharding oracle прошли; delta specs синхронизированы, change
  архивирован.
- 2026-08-31 post-archive core прошёл `22/22` за `206.012s`; следующий этап —
  отдельный independent review, карточка остаётся в `3.inprogress`.
- 2026-08-31 normalized deterministic preflight сообщил
  `ready-for-llm-review`; independent review/verdict не запускались.
- 2026-08-31T19:45:10Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
