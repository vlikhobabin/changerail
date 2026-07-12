## Context

`scripts/changerail_delivery_manifest.py` выводит `committable_paths` из git
status и передает их в `staging-plan`, который publish использует как initial
scoped staging proposal. Прежняя реализация читала `git status --porcelain` как
текст, делила вывод по строкам и разбирала renames через поиск `" -> "`. Это
небезопасно для quoted paths, Unicode paths, spaces и filenames, которые
содержат arrow text буквально. Git также может показывать untracked directory
как directory path в обычном porcelain output, что расширяет publish scope за
пределы card-owned files.

## Goals / Non-Goals

**Goals:**
- Использовать NUL-delimited git status output для manifest derivation.
- Сохранять repository-relative path strings ровно так, как Git сообщает их
  после decoding bytes через local filesystem encoding.
- Разворачивать untracked directories до точных untracked non-ignored file
  paths.
- Сохранять staging plans deterministic и auditable.

**Non-Goals:**
- Не менять public manifest schema id.
- Не делать publish доверяющим manifest без повторной проверки workspace state.
- Не добавлять consumer-project-specific path policy.

## Decisions

- Использовать `git status --porcelain=v1 -z --untracked-files=all` как source
  of truth. Это оставляет rename source/target pairs machine-readable и
  заставляет Git перечислять untracked directories как files, когда он может их
  enumeratе.
- Decode status records через `os.fsdecode` из raw bytes. Это убирает shell
  quoting artifacts и оставляет Python paths usable для repository-relative
  JSON output.
- Писать manifest и JSON CLI payloads с ASCII escaping. Это сохраняет
  `surrogateescape` path strings для valid non-UTF-8 Linux path bytes без raw
  surrogate в UTF-8 file и позволяет проверить byte round-trip через
  `os.fsencode`.
- Представлять renames через `source_path` и `target_path`, сохраняя `path` как
  target для compatibility. Deletions сохраняют `source_path` и `path` как
  removed path.
- Отклонять untracked status entry, который после `--untracked-files=all` все
  еще указывает на directory или non-regular path, потому что staging такого
  path может включить unrelated files.

## Risks / Trade-offs

- [Risk] Git porcelain v1 rename records компактны, и их легко разобрать
  неверно. Mitigation: изолировать parsing в маленьких helpers и покрыть
  rename, delete и literal ` -> ` path fixtures.
- [Risk] Filesystem decoding может дать `surrogateescape` path strings для
  valid non-UTF-8 Linux filenames. Mitigation: писать JSON с ASCII escaping и
  тестировать byte round-trip через `os.fsencode`, включая байт `0xff`.
- [Risk] Exact file expansion может дать больше manifest entries. Mitigation:
  deterministic ordering сохраняет review и publish output читаемыми.
