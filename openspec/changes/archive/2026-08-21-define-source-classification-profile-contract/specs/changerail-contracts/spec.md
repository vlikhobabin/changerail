## ADDED Requirements

### Requirement: Versioned source classification profile
ChangeRail MUST валидировать `changerail.source-classification-profile.v1` как
data-only envelope со stable id/version, compatible classification payload и
bounded repository-name detection signals. Contract MUST отклонять
absolute/traversing paths, executable behavior, commands, imports и network
sources.

#### Scenario: Built-in и integration profiles используют общую валидацию
- **WHEN** tracked built-in generic profile или explicitly supplied local
  integration profile содержит safe rules/signals
- **THEN** оба валидируются одной public schema
- **AND** ни один source не может загрузить executable code или network data

#### Scenario: Unsafe profile отклоняется
- **WHEN** profile содержит machine-absolute paths, traversal, command, URL,
  dynamic module или unsupported measurement strategy
- **THEN** schema/semantic validation fail closed
- **AND** classification из него не выводится

### Requirement: Stable profile checksum and identity
ChangeRail MUST вычислять `sha256:<hex>` из documented canonical serialization
полного validated profile. Одинаковые id/version с разным checksum MUST
считаться immutable-version conflict.

#### Scenario: Equivalent profile загружен дважды
- **WHEN** identical profile content загружается из supported sources
- **THEN** id, version и checksum совпадают
- **AND** source report различает source kind без записи absolute machine path

#### Scenario: Published profile version меняет content
- **WHEN** profile id/version совпадает с known profile, но canonical checksum
  отличается
- **THEN** validation/merge блокируется
- **AND** maintainer MUST выпустить новую profile version

### Requirement: Deterministic profile merge
Несколько selected profiles MUST merge в declared order с deterministic
canonical output, deduplicate equivalent rules и fail closed для overlapping
rules с conflicting measurements или разным content под одним source-kind id.

#### Scenario: Compatible profiles объединяются
- **WHEN** selected profiles имеют disjoint или exactly equivalent rules
- **THEN** merge создает одну stable source classification и ordered provenance
- **AND** repeated merge имеет тот же checksum/output

#### Scenario: Measurement conflict обнаружен
- **WHEN** overlapping suffix/root rules классифицируют один source разными
  measures `lines` и `xml-structure`
- **THEN** merge останавливается с machine-readable conflict
- **AND** не разрешает конфликт по discovery или file-system order

### Requirement: Classification profile provenance compatibility
`changerail.source-classification.v1` MUST разрешать optional ordered profile
identity/checksum/source provenance и normalized declared override paths,
сохраняя final source kinds/non-production roots единственными rules,
используемыми review preflight.

#### Scenario: Legacy project file не имеет provenance
- **WHEN** existing schema-valid classification не содержит profile provenance
- **THEN** он остается valid, а preflight behavior не меняется
- **AND** profile-aware diagnostics сообщает provenance как unavailable

#### Scenario: Materialized file объявляет overrides
- **WHEN** final classification отличается от profile baseline только в
  declared normalized override paths
- **THEN** report определяет differences как project overrides
- **AND** values читаются из final classification, а не дублируются в provenance
