## 1. Portable launcher

- [x] 1.1 Реализовать canonical repo-root resolution, forced
  `CODEX_WORKDIR`/`-C` и безопасное TOML encoding для dynamic project trust и
  filesystem MCP overrides в `bin/codex`.
- [x] 1.2 Добавить `CHANGERAIL_CODEX_BIN`, non-recursive PATH resolution и
  fail-closed diagnostics для missing, invalid и self-referential dispatcher.

## 2. Regression coverage и docs

- [x] 2.1 Добавить credential-free `scripts/smoke-codex-launcher.py` для
  `/opt/changerail` config regression, arbitrary quoted temporary root,
  ambient workdir override, dispatcher override/PATH fallback и failure cases.
- [x] 2.2 Включить focused smoke в exact `core` inventories runner/oracle и
  синхронизировать release CI requirement.
- [x] 2.3 Обновить `AGENTS.md` и `docs/compatibility.md`: stable consumer path,
  portable development checkout, launcher scope и официальный CLI override
  contract без version/release bump.

## 3. Verification

- [x] 3.1 Выполнить focused smoke, Python compile/lint, TOML/JSON parsing и
  `./bin/openspec validate --all --strict`.
- [x] 3.2 Выполнить `git diff --check`, public-surface scans включая history и
  полный релевантный `python3 scripts/run-release-baseline.py`; проверить, что
  runtime evidence остаётся ignored.
- [x] 3.3 Сопоставить реализацию со всеми requirements/scenarios, проверить
  review-ready diff и сохранить concise verification result перед sync/archive.

## 4. Independent-review remediation

- [x] 4.1 Добавить fail-closed argv policy для protected config/root options с
  сохранением unrelated overrides во всех поддерживаемых global/`exec` forms.
- [x] 4.2 Исправить lossless canonical-root и полную POSIX PATH empty/relative
  component semantics.
- [x] 4.3 Перевести helper resolution на fixed paths и связать dispatcher
  validation/exec одним Linux `/proc/self/fd` inode; доказать real Node wrapper.
- [x] 4.4 Расширить focused smoke точными argv/env/diagnostic assertions для
  whitespace, recursion, PATH, policy, hijack, TOCTOU и dispatcher matrix.
- [x] 4.5 Выполнить полный post-remediation verify, sync main specs и повторный
  archive без active changes.

## 5. Independent re-review remediation

- [x] 5.1 Воспроизвести RED для nested `exec -c` layer loss, filesystem sibling
  overrides, `--ignore-user-config` bypass и fake-only smoke oracle.
- [x] 5.2 Перенести trust и полный filesystem subtree в effective `exec` layer,
  защитить весь subtree/config-source bypass и сохранить lossless user argv.
- [x] 5.3 Добавить deterministic effective-layer oracle и actual credential-free
  Codex config/`exec` probes для profile, Node wrapper и MCP scope.
- [x] 5.4 Синхронизировать delta/main specs и docs, включая `24-item`, затем
  выполнить focused и полный verification floor перед повторным archive.
