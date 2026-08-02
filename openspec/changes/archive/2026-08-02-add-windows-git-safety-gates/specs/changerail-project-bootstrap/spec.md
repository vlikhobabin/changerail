## ADDED Requirements

### Requirement: Windows fallback Git proof gate
Bootstrap MUST require concrete Git safety evidence before accepting Windows
junction fallback proof, and MUST preserve the same fail-closed behavior for
symlink fallback fixtures that depend on Git staging safety.

#### Scenario: Junction fallback proof includes Git evidence
- **WHEN** an operator requests Windows junction fallback wiring
- **THEN** bootstrap accepts the fallback proof only when it includes concrete
  passed evidence for Git porcelain status, dry-run add and index inspection
- **AND** missing, status-only or hash-only evidence exits non-zero before
  reporting success

#### Scenario: Unsafe Git evidence is rejected
- **WHEN** fallback proof evidence indicates that Git would stage ChangeRail
  source, ignored runtime state, credentials or out-of-scope files
- **THEN** bootstrap rejects the fallback before creating or reporting usable
  Windows link wiring

### Requirement: Windows wiring cleanup and ownership negative coverage
Bootstrap smoke MUST cover rename, update, uninstall and partial cleanup
scenarios without hiding project-owned source.

#### Scenario: Partial cleanup is link-aware
- **WHEN** Windows wiring setup fails after creating generated, symlink or
  junction-style artifacts
- **THEN** cleanup removes only current-run-owned or generated-owned paths
- **AND** it does not recurse into link targets or remove project-owned files

#### Scenario: Project-owned source remains visible
- **WHEN** smoke verifies minimal ignore rules for a Windows wiring fixture
- **THEN** project-owned source files remain visible to Git status or dry-run
  evidence
- **AND** ignored runtime/auth files remain ignored or forbidden
