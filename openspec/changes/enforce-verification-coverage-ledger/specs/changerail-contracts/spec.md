## ADDED Requirements

### Requirement: Manifest coverage summary
`changerail.delivery-manifest.v1` MUST поддерживать concise verification
coverage summary, который ссылается на ignored ledger path/fingerprint и
сообщает configured/applicable/covered/missing/invalid counts без map content
или raw evidence.

#### Scenario: Delivery обновляет coverage summary
- **WHEN** actual manifest scope reconciled с configured map и ledger
- **THEN** manifest записывает bounded counts и ledger reference
- **AND** evidence contents остаются в ignored evidence index/output paths

#### Scenario: Summary заявляет complete при stale ledger
- **WHEN** manifest summary сообщает отсутствие missing entries, но ledger
  fingerprints не совпадают с current map/card/scope/review target
- **THEN** deterministic preflight отклоняет summary
- **AND** independent review не запускается на его основании
