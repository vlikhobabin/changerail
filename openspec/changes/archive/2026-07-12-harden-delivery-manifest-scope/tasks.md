## 1. Manifest Parser

- [x] 1.1 Заменить line-oriented git status parsing на `--porcelain=v1 -z --untracked-files=all` parsing в `scripts/changerail_delivery_manifest.py`.
- [x] 1.2 Сохранить точные add/modify/delete/rename operation entries, включая `source_path` и `target_path`, где они обязательны.
- [x] 1.3 Отклонять unsafe untracked directory или non-regular path entries вместо добавления directory-wide staging paths.

## 2. Regression Coverage

- [x] 2.1 Расширить `scripts/smoke-delivery-manifest-derive.py` fixtures для spaces, quotes, Unicode, literal ` -> `, non-UTF-8 path byte round-trip, rename, delete и нескольких untracked files в одном directory.
- [x] 2.2 Покрыть mixed pre-existing dirty state в manifest derivation и staging-plan output.

## 3. Docs And Verification

- [x] 3.1 Обновить delivery manifest docs/spec references с exact path и conservative untracked scope behavior.
- [x] 3.2 Run `python3 scripts/smoke-delivery-manifest-derive.py`.
- [x] 3.3 Run `openspec validate harden-delivery-manifest-scope --strict`.
- [x] 3.4 Run `git diff --check`.
