## ADDED Requirements

### Requirement: Review preflight counts declared Designer XML structurally
The deterministic review preflight MUST count Designer XML only when a valid
consumer source-classification rule proves that the XML path belongs to a
production Designer XML source kind. The preflight MUST NOT treat generic
`.xml` paths as production source by suffix alone.

#### Scenario: Production Designer XML is classified
- **WHEN** a scoped payload adds Designer XML under a declared production
  Designer XML source root
- **THEN** preflight counts the file through the Designer XML measure strategy
- **AND** the source-kind breakdown identifies Designer XML as a production
  contribution

#### Scenario: Generic XML remains non-production
- **WHEN** a scoped payload adds `.xml` files under schemas, templates,
  fixtures, examples, docs, OpenSpec or an unclassified path
- **THEN** those XML files do not contribute to production complexity
- **AND** they do not make the payload `investigation-required` by suffix alone

### Requirement: Designer XML complexity is fail-closed and explainable
Designer XML production complexity MUST use an effective structural measure
instead of unconditional raw XML line count when the helper can measure the XML
safely. If the helper cannot safely prove structural complexity, it MUST either
fall back to raw added lines or block preflight; it MUST NOT silently report
zero for classified production Designer XML.

#### Scenario: Verbose Designer XML has bounded structural complexity
- **WHEN** a classified Designer XML addition has raw added lines above the
  default or authorized LOC ceiling but measured structural complexity within
  the applicable ceiling
- **THEN** preflight may continue to the declared risk-appropriate review route
- **AND** the result reports both raw added lines and effective structural
  complexity for the Designer XML source kind

#### Scenario: Designer XML exceeds effective ceiling
- **WHEN** classified Designer XML effective complexity exceeds the applicable
  default or published authorization ceiling
- **THEN** preflight returns `investigation-required`
- **AND** the complexity guard reasons identify the exceeded effective ceiling

#### Scenario: Designer XML cannot be measured safely
- **WHEN** classified production Designer XML is malformed or the structural
  measure cannot be computed conservatively
- **THEN** preflight uses raw added lines as the effective contribution or
  returns `blocked`
- **AND** the result explains the fallback or blocker in source-kind detail

### Requirement: Mixed 1C payload complexity is itemized
The preflight result MUST itemize mixed production payloads so maintainers can
see how BSL and Designer XML contribute to the guard without inspecting raw
source content.

#### Scenario: BSL and Designer XML share a payload
- **WHEN** a scoped payload contains declared production BSL and Designer XML
  changes
- **THEN** `added_production_loc` reflects their aggregate effective
  contribution
- **AND** source-kind detail reports separate BSL and Designer XML entries with
  path counts, raw added lines, effective contribution and measure strategy
