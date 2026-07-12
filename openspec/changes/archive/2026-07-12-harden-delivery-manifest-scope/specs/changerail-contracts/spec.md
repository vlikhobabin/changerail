## ADDED Requirements

### Requirement: Точный вывод delivery manifest paths
Delivery manifest derivation MUST использовать machine-readable git status data
и MUST записывать точные repository-relative paths для card-owned additions,
modifications, deletions и renames без shell quoting artifacts.

#### Scenario: Manifest точно записывает допустимые символы path
- **WHEN** manifest derivation видит changed paths со spaces, quotes, Unicode
  characters или literal ` -> ` text
- **THEN** `committable_paths` записывает repository-relative paths без
  добавленных quotes, lossy splitting или arrow-based rewrite

#### Scenario: Manifest сохраняет non-UTF-8 path bytes
- **WHEN** manifest derivation видит repository path с valid non-UTF-8 bytes в
  Linux workspace
- **THEN** JSON output остается valid UTF-8 и сохраняет path так, что
  filesystem byte round-trip через `os.fsencode` восстанавливает исходные bytes

#### Scenario: Manifest записывает source и target для rename
- **WHEN** manifest derivation видит card-owned rename
- **THEN** manifest записывает `operation: rename`, `source_path` и
  `target_path`

#### Scenario: Manifest записывает deleted path
- **WHEN** manifest derivation видит card-owned delete
- **THEN** manifest записывает `operation: delete` и `source_path` для removed
  path

### Requirement: Консервативный untracked manifest scope
Delivery manifest derivation MUST NOT включать directory-wide untracked path в
`committable_paths`, когда такой path может stage-ить unrelated files.

#### Scenario: Untracked directory содержит несколько files
- **WHEN** manifest derivation видит untracked files в одном directory
- **THEN** `committable_paths` содержит каждый точный file path вместо parent
  directory

#### Scenario: Untracked path нельзя безопасно перечислить
- **WHEN** manifest derivation не может представить untracked directory или
  non-regular path как точные file paths
- **THEN** helper validation завершается fail до записи staging proposal
