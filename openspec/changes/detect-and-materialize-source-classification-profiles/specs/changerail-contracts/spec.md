## ADDED Requirements

### Requirement: Read-only source profile detection
ChangeRail MUST предоставлять machine-readable command `detect`, который
оценивает validated profile path signals относительно tracked `HEAD` или
explicit Git tree snapshot и сообщает candidates, matched signals, bounded
confidence, ambiguities и recommended action без изменения файлов.

#### Scenario: Detection выполняется в dirty working tree
- **WHEN** working tree добавляет profile marker, которого нет в tracked `HEAD`,
  и explicit snapshot не передан
- **THEN** detection оценивает `HEAD` и не использует dirty marker
- **AND** review preflight risk/classification не меняются

#### Scenario: Совпадают multiple candidates
- **WHEN** mixed repository совпадает с signals нескольких profiles с equal или
  overlapping confidence
- **THEN** JSON output перечисляет все candidates/ambiguities со stable scores
- **AND** command не выбирает и не materialize один автоматически

### Requirement: Explicit preview-first profile materialization
ChangeRail MUST materialize source classification только из explicitly selected
schema-valid profiles. Default materialize MUST выполнять preview; mutation
MUST требовать `--write`, повторно валидировать inputs и атомарно создавать
schema-valid project file.

#### Scenario: Новый project подтверждает profile
- **WHEN** target file отсутствует и оператор сначала preview, затем write exact
  profile selection
- **THEN** helper создает `.changerail/source-classification.yaml` с final rules
  и ordered id/version/checksum/source provenance
- **AND** existing review preflight валидирует и использует этот file

#### Scenario: Existing file отличается
- **WHEN** project classification уже существует с другими effective rules или
  provenance
- **THEN** materialize завершается non-zero с bounded semantic diff и status
  migration required
- **AND** не overwrite и не reformat existing file

#### Scenario: Repeated materialization идемпотентна
- **WHEN** same profile selection и inputs направлены на already matching file
- **THEN** command сообщает no change и успешно завершается
- **AND** file bytes/effective rules остаются stable

### Requirement: Candidate has no classification authority
Detected, но unaccepted profile MUST NOT влиять на `added_production_loc`, risk
tier, investigation decision или source breakdown. На current review preflight
может влиять только tracked schema-valid
`.changerail/source-classification.yaml`.

#### Scenario: High-confidence candidate не materialized
- **WHEN** detect сообщает high-confidence domain profile, но project file
  отсутствует
- **THEN** preflight продолжает работу с current built-in classifier
- **AND** candidate report является только advisory evidence
