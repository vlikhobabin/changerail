## 1. Fresh regression floor

- [x] 1.1 Подтвердить clean implementation scope относительно safe base
  `16d441e8b5f4d8a415ae011e46cce5b3863a1010`; не импортировать старые
  unpublished card/archives, runtime reports или raw logs.
- [x] 1.2 Добавить public-safe `scripts/smoke-public-surface-history.py` с
  минимум 250 commits/20 paths, reused blobs, delete/rename, merge resolution,
  binary/invalid UTF-8, multi-path finding, excluded root и unrelated ref.
- [x] 1.3 Добавить RED semantic/process-count oracle против safe-base scanner,
  включая scan-once, complete commit/path attribution и максимум три Git
  process launches.
- [x] 1.4 Добавить отдельный raw mode/framing oracle для valid transitions и
  malformed marker/header/path, mode/status/OID, truncation и batch response.
- [x] 1.5 Добавить отдельный lifecycle oracle для timeout, non-zero exit,
  premature EOF и pipe failure на resolve/log/batch boundaries; проверить
  generic redacted non-zero outcome без raw content leakage.
- [x] 1.6 Классифицировать focused fixture как non-production test в
  `.changerail/source-classification.yaml`.

## 2. Bounded history scanner

- [x] 2.1 Реализовать exact full `HEAD^{commit}`/shallow preflight и один
  `--format=tformat:%x1e%H --raw -z --no-abbrev` history stream без unrelated
  refs.
- [x] 2.2 Реализовать byte-level raw state machine с mode/type/status
  validation и unique-blob commit/path attribution для regular/symlink blobs.
- [x] 2.3 Реализовать один persistent size-delimited `cat-file --batch` reader
  с exact oid/type/size/trailing-LF validation и bounded cleanup.
- [x] 2.4 Сохранить current-tree rules, binary/invalid UTF-8 behavior, secret
  redaction и `changerail.public-surface-scan.v1`; довести focused regression до
  GREEN под `timeout 30s`.

## 3. Exact release suite ownership

- [x] 3.1 Разделить `scripts/run-release-baseline.py` на default `core` и
  explicit `extended` с deterministic ordered `--list`, без режима `all`.
- [x] 3.2 Закрепить exact 22-item core и 12-item extended inventories из
  design; исключить Windows diagnostics из обеих suites и оставить
  `python3 scripts/smoke-delivery-runner.py` только в extended.
- [x] 3.3 Обновить default `.github/workflows/changerail-ci.yml` для exact
  core-only invocation `python3 scripts/run-release-baseline.py` и
  `fetch-depth: 0`; добавить scheduled/manual extended workflow с
  `fetch-depth: 0` и exact invocation
  `python3 scripts/run-release-baseline.py --suite extended`.
- [x] 3.4 Усилить `scripts/smoke-release-ci.py`: exact order/set, uniqueness,
  missing/extra/overlap rejection, both workflow triggers/full checkout и
  negative oracle для ошибочного core ownership one-command regression.
- [x] 3.5 Обновить `docs/release-discipline.md` и `docs/compatibility.md`:
  Linux-focused default admission, обязательная отдельная extended regression,
  exact one-command ownership и opt-in Windows diagnostics.
- [x] 3.6 Синхронизировать `changerail-release-ci` и
  `changerail-release-discipline` main specs из delta specs, сохранив финальное
  normative ownership только за extended.

## 4. Verification and fresh handoff

- [x] 4.1 Запустить `python3 scripts/public-surface-scan.py --self-test` и
  `timeout 30s python3 scripts/smoke-public-surface-history.py`.
- [x] 4.2 Запустить core/extended inventory listing и
  `python3 scripts/smoke-release-ci.py`; подтвердить exact ordered counts,
  disjointness, negative removal/extra/overlap cases и `fetch-depth: 0`.
- [x] 4.3 Запустить `timeout 300s python3 scripts/run-release-baseline.py` и
  exact extended gate
  `python3 scripts/run-release-baseline.py --suite extended` в fresh checkout.
- [x] 4.4 Явно запустить retained opt-in Windows entrypoint и wiring Git-safety
  diagnostics либо записать public-safe обоснование неприменимости без
  изменения текущей Linux-focused claim.
- [x] 4.5 Запустить `bin/openspec validate
  replace-bounded-public-history-scan-and-align-release-suites --strict`,
  `bin/openspec validate --all --strict`, `python3
  scripts/public-surface-scan.py`, `python3 scripts/public-surface-scan.py
  --history` и whitespace checks с включением untracked files.
- [x] 4.6 Подтвердить не более 300 added production LOC для всего coherent unit
  и отсутствие новой authority, dependency, release-ref CLI или wire/report
  protocol.
- [x] 4.7 Собрать fresh scoped manifest и concise retained evidence только для
  replacement payload, архивировать change через `changerail-do` и передать
  payload новому independent high-effort reviewer; source manifest/evidence/
  verdict повторно не использовать.

## Delivery evidence

- Operator-authorized remediation сохранил 69 scenarios как exact два shard-а
  `39 + 30`; fresh-checkout `timeout 300s python3
  scripts/run-release-baseline.py` завершился `0`, `22/22`, за `198.548s`, а
  вложенный `python3 scripts/smoke-verify-project.py` сообщил `69/69`.
  Evidence: `.runtime/blocker-remediation/20260831T181506Z/` (`preparation.txt`,
  `core-result.txt`, `core.log`, source/fresh status и SHA-256 manifests).
- `python3 scripts/smoke-verify-project-sharding.py` завершился `0`: exact
  parity/order, single scenario failure, exception, crash, timeout, missing,
  duplicate, malformed result, isolation и cleanup GREEN. Отдельный RED в этой
  resumed session не запускался, потому что remediation уже существовал в
  operator-authorized handoff; injected fail-closed fault cases наблюдают
  intended process boundary и ломаются при заявленном regression.
- В SHA-256-matched fresh checkout `python3
  scripts/run-release-baseline.py --suite extended` завершился `0`, `12/12`,
  за `225.467s`.
- `python3 scripts/smoke-windows-entrypoints.py` завершился `0`, `67/67`;
  `python3 scripts/smoke-windows-wiring-git-safety.py` завершился `0`, `6/6`.
  Это opt-in diagnostics и они не расширяют Linux-focused release claim.
- `bin/openspec validate
  replace-bounded-public-history-scan-and-align-release-suites --strict`,
  `python3 -m json.tool .mcp.json`, TOML parse `.codex/config.toml`, оба
  public-surface scans и temporary-index whitespace check завершились `0` до
  archive; current/history scans сообщили `1305 files, 0 findings`.
- Delta requirements idempotently совпали с main specs для обеих capabilities;
  `bin/openspec validate changerail-release-ci --strict`, `bin/openspec
  validate changerail-release-discipline --strict`, `bin/openspec validate
  --all --strict` и `git diff --check` завершились `0` после sync.
- После sync `python3 scripts/smoke-release-ci.py` и повторный strict active
  change validation завершились `0`.
- `bin/openspec archive
  replace-bounded-public-history-scan-and-align-release-suites --yes` завершился
  `0`; archive path:
  `openspec/changes/archive/2026-08-31-replace-bounded-public-history-scan-and-align-release-suites/`.
  После bounded EOF-whitespace fix cycle 1 `bin/openspec validate --all
  --strict` и `git diff --check` завершились `0`.
- Финальный post-archive `timeout 300s python3
  scripts/run-release-baseline.py` завершился `0`, `22/22`, за `206.012s`,
  включая `69/69` verify-project и current/history scans `1305/0`.
- Delivery manifest derived/validated; working-tree scope-check сообщил
  `ok=true`, `missing=[]`, `extra=[]`, `mismatched=[]`.
- `bin/changerail-review-verdict preflight <card> --workspace . --normalize
  --output <runtime-preflight> --json` завершился `0` с outcome
  `ready-for-llm-review`, complexity `272/300` и всеми deterministic checks
  GREEN; independent review не запускался.
- Retained evidence index:
  `.runtime/changerail/evidence/replace-bounded-public-history-scan-and-align-release-suites/index.json`.
