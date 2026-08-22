## ADDED Requirements

### Requirement: Lifecycle skill coverage responsibilities
Canonical skills `changerail-ff`, `changerail-do` и `changerail-review` MUST
обрабатывать project coverage map через единый plan/ledger contract и MUST NOT
копировать raw evidence или создавать alternative acceptance verdict.

#### Scenario: Fast-forward планирует configured coverage
- **WHEN** `changerail-ff` обрабатывает card в project с valid map
- **THEN** он пишет schema-valid per-change coverage reference после определения
  proposal/design scope
- **AND** selected ids/hash references соответствуют map/card sources

#### Scenario: Review получает incomplete ledger
- **WHEN** independent review видит applicable rule с missing/invalid evidence
  или oracle, не наблюдающий claimed boundary
- **THEN** skill записывает blocker evidence/test-adequacy finding
- **AND** не отмечает acceptance pass только по наличию path/command
