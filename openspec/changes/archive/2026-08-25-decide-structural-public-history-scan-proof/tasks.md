## 1. Опубликовать structural decision contract

- [x] 1.1 Синхронизировать delta `changerail-release-ci`, сохранив published
  fixture-v2 decisions/certification и forensic evidence неизменными, но
  supersede-нув их authority только для future structural delivery.
- [x] 1.2 Проверить, что current requirement фиксирует exact two-child traversal,
  invocation-local object и `(blob,path)` memo, strict fail-closed parsing,
  запрет persistent cross-run cache/state, no-mutation refs/worktree/index с
  connected independent before/after exact oracle, independent actual tuple
  proof, real-Git parity/fault cases, observational `time -v`, final
  history/baseline и `fetch-depth: 0`.
- [x] 1.3 Зафиксировать exact ordered authorization/successor references,
  authorization ceiling `301`, protocol allowance `false` и independent
  implementation limit `<=300` production LOC относительно exact `ccccb625`.
- [x] 1.4 Подтвердить classification scope: изменены только source card,
  OpenSpec artifacts и synced spec; production/test/runtime additions равны
  `0` LOC, successors и implementation не создаются.

## 2. Проверить decision-only payload

- [x] 2.1 Выполнить `bin/openspec validate
  decide-structural-public-history-scan-proof --strict` и
  `bin/openspec validate --all --strict`.
- [x] 2.2 Проверить JSON/TOML через `python3 -m json.tool .mcp.json` и
  `tomllib.load` для `.codex/config.toml`.
- [x] 2.3 Выполнить только current scan
  `python3 scripts/public-surface-scan.py` и
  `bin/changerail-source-classification --json check`; history scan, benchmark
  и full baseline не запускать для decision payload.
- [x] 2.4 Проверить `git diff --check`, whitespace всех новых untracked files,
  delivery-manifest derive/scope-check и normalized review preflight; ожидаемые
  board/archive readiness gates закрыть в DO до review.
- [x] 2.5 Синхронизировать card result/archive metadata и архивировать только
  decision change после успешной проверки; review, commit, push и successor
  creation оставить последующим фазам.
