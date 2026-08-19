## ADDED Requirements

### Requirement: Explicit lockless consumer wiring adoption
`bootstrap-project` MUST provide an explicit existing-project adoption mode for
legacy consumers that have ChangeRail wiring but lack
`openspec/changerail-consumer-lock.json`. Plain `--refresh-wiring` MUST remain
fail-closed when the consumer lock is missing.

#### Scenario: Refresh without lock remains blocked
- **WHEN** an operator runs existing-project `--refresh-wiring` for a consumer
  without `openspec/changerail-consumer-lock.json`
- **THEN** bootstrap exits non-zero before mutation
- **AND** the diagnostic identifies the explicit lockless adoption command as
  the opt-in migration path

#### Scenario: Operator previews lockless adoption
- **WHEN** an operator runs existing-project lockless adoption with `--dry-run`
- **THEN** bootstrap prints an inventory of allowlisted ChangeRail-owned skills,
  commands and helper wrappers that will be kept, added or rejected
- **AND** it does not create a consumer lock, wiring manifest or helper artifact

#### Scenario: Successful lockless adoption writes tracked intent
- **WHEN** lockless adoption proves a single ChangeRail source root, compatible
  backend/path mode and clean source revision
- **THEN** bootstrap writes a schema-valid
  `openspec/changerail-consumer-lock.json`
- **AND** any generated-copy ownership metadata required by the selected backend
  is schema-valid

### Requirement: Lockless adoption ownership gates
Lockless adoption MUST accept only allowlisted ChangeRail-owned wiring and MUST
fail closed without partial mutation on dangling, mixed-root, mixed-mode,
regular-file, project-owned, undeclared or scope-escaping conflicts.

#### Scenario: Existing correct symlinks are accepted
- **WHEN** a lockless POSIX consumer has allowlisted symlinks that resolve under
  one declared ChangeRail source root
- **THEN** adoption accepts those symlinks as keep decisions
- **AND** missing newly supported helpers are add decisions using the inferred
  backend and path mode

#### Scenario: Mixed roots block adoption
- **WHEN** allowlisted wiring resolves to more than one ChangeRail source root
- **THEN** adoption exits non-zero before writing the lock
- **AND** diagnostics identify mixed-root ownership without printing private
  absolute paths

#### Scenario: Project-owned conflict blocks adoption
- **WHEN** an allowlisted destination contains a regular file, directory or
  undeclared link that is not proven ChangeRail-owned
- **THEN** adoption exits non-zero without replacing that content
- **AND** no current-run helper, lock or manifest remains after rollback

#### Scenario: Unrelated dirty state blocks adoption
- **WHEN** the consumer has unrelated dirty tracked files before adoption
- **THEN** adoption exits non-zero before mutation
- **AND** diagnostics require the operator to separate project work from wiring
  migration

### Requirement: Platform policy for lockless adoption
Lockless adoption MUST make POSIX symlink and Windows generated-copy, symlink or
junction policies explicit. Unsupported or ambiguous platform inference MUST
block adoption with remediation.

#### Scenario: POSIX path mode is inferred
- **WHEN** accepted POSIX symlinks all use one source root and one path mode
- **THEN** the adopted lock records backend `symlink` and the inferred
  `absolute` or `relative` path mode
- **AND** missing helper symlinks are created with that same mode

#### Scenario: Windows generated ownership is present
- **WHEN** a Windows generated-copy consumer has verifier-readable generated
  ownership metadata for existing artifacts
- **THEN** adoption uses generated-copy policy and updates only generated-owned
  wiring metadata and missing generated helpers

#### Scenario: Windows ownership cannot be proven
- **WHEN** Windows wiring uses generated files, symlinks or junctions without
  required ownership metadata or fallback proof
- **THEN** adoption exits non-zero before mutation
- **AND** diagnostics identify the required proof or manual regeneration path
