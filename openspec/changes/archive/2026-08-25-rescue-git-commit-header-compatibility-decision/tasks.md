## 1. Rescue Decision Contract

- [x] 1.1 Синхронизировать complete Git-header requirement в
  `openspec/specs/changerail-release-ci/spec.md` после complete existing
  `Consumer Codex auth setup smoke coverage` requirement, не изменяя
  его heading и scenarios.
- [x] 1.2 Сверить first-tree/first-`SP`/blank-fold grammar, exact bounds,
  `95/95` source и `98/98` all-ref populations, all digests и aggregate signed/
  fold observations между card, proposal, design и delta spec.
- [x] 1.3 Сверить exact six-field authorization object: rescue investigation ID,
  unchanged replacement, ceiling `301` и protocol `false`; не добавлять
  authorization/replacement card и не переносить exhausted artifacts.

## 2. Ownership And Scope Oracles

- [x] 2.1 Проверить heading-sliced main spec oracle: auth requirement имеет
  ровно два scenarios и включает `Smoke keeps credentials out of output`;
  Git-header requirement имеет ровно восемь scenarios и не владеет
  auth-fixture scenario.
- [x] 2.2 Подтвердить, что scoped payload содержит только rescue card,
  его OpenSpec change/archive и corrected main release-CI spec, а added
  production/test/runtime LOC равен `0`.

## 3. Documentation Verification

- [x] 3.1 Выполнить strict target/capability/all OpenSpec validation и `openspec show`
  JSON ownership assertion.
- [x] 3.2 Проверить `.mcp.json` через `python3 -m json.tool`,
  `.codex/config.toml` через `tomllib`, выполнить current-only
  `python3 scripts/public-surface-scan.py` и source classification.
- [x] 3.3 Выполнить `git diff --check`, explicit whitespace checks для
  untracked files, scoped status/diff, manifest derive/scope и normalized
  ordinary/high preflight; не запускать history scan, benchmark или full
  release baseline.

## Verification Notes

RED evidence неприменимо: change публикует docs-only decision и не меняет
executable behavior.

## Verification Notes

- `bin/openspec validate rescue-git-commit-header-compatibility-decision --strict`,
  `bin/openspec validate changerail-release-ci --strict` и
  `bin/openspec validate --all --strict` прошли; после archive strict-all
  подтвердил `23/23` specs.
- Heading-sliced oracle подтвердил `auth=2`, presence `Smoke keeps credentials
  out of output`, `git-header=8`, отсутствие `fake auth marker` в Git-header
  block и placement сразу после auth requirement. Byte-exact synced delta имеет
  `sha256:ed38b97d4d42572ef5b1b12aacd6d4a55d9ca1c3c40bf4d69aba8f4f0235ada0`.
- `python3 -m json.tool .mcp.json`, `tomllib` для `.codex/config.toml`,
  `python3 scripts/public-surface-scan.py` (`1342/0`) и
  `bin/changerail-source-classification --workspace . --json check`
  (`blocking=0`, `advisory=0`) прошли.
- `git diff --check`, explicit whitespace check, manifest derive/scope и
  normalized ordinary/high preflight выполнены. До archive preflight отклонил
  только ожидаемый active-not-archived gate; final archived preflight указан в
  board handoff. History scan, benchmark и full release baseline не запускались.
