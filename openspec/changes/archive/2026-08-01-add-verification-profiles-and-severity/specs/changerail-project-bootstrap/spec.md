## ADDED Requirements

### Requirement: Bootstrap renders default verification profile policy
Bootstrap MUST render generated consumer OpenSpec config with an explicit
verification policy that preserves the strict all-surfaces default.
The generated policy MUST be tracked project configuration, not ignored runtime
state.

#### Scenario: Generated project receives strict verification policy
- **WHEN** `bin/bootstrap-project /opt/example-project --name example-project
  --kind generic` renders a consumer project
- **THEN** `openspec/config.yaml` declares the default verification profile as
  strict all-surfaces
- **AND** `bin/verify-project /opt/example-project` treats missing canonical
  ChangeRail surfaces as blocking failures unless the tracked project policy is
  changed

#### Scenario: Bootstrap smoke verifies generated policy
- **WHEN** `python3 scripts/smoke-bootstrap-project.py` runs
- **THEN** it verifies the generated default verification profile policy through
  `bin/verify-project`

### Requirement: Bootstrap guidance documents profile override boundary
Bootstrap guidance MUST explain that consumers may opt into Codex-only or other
profile policies only by editing tracked project policy, and that targeted
card-owned validation cannot be made non-blocking.

#### Scenario: Operator reads generated guidance
- **WHEN** an operator inspects generated consumer guidance
- **THEN** the guidance identifies `required`, `optional` and `forbidden`
  surface states
- **AND** it states that profile policy can produce
  `pass-with-diagnostics` only for non-blocking findings
- **AND** it states that targeted card-owned OpenSpec validation remains
  mandatory
