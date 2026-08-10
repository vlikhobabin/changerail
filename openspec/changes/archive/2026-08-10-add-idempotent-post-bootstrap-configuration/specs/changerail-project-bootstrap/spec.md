## ADDED Requirements

### Requirement: Bounded existing-project configuration mode
`bootstrap-project` MUST provide an explicit existing-project mode that performs
only allowlisted auth-link and manifest-owned wiring actions without rendering
or overwriting project-owned templates. The mode MUST be idempotent and MUST
fail closed on unsupported flags, unrelated dirty state or ownership conflict.

#### Scenario: Operator configures auth after bootstrap
- **WHEN** an operator invokes existing-project mode with a valid auth-link
  source
- **THEN** bootstrap creates or confirms the ignored project-local auth symlink
- **AND** it does not read or print credential contents

#### Scenario: Desired configuration already exists
- **WHEN** the auth link and owned wiring already match declared intent
- **THEN** repeated configuration succeeds without changing tracked files

#### Scenario: Project-owned content conflicts
- **WHEN** an allowlisted destination contains a real project-owned file or
  undeclared link
- **THEN** configuration exits non-zero without replacing that content

#### Scenario: Configure mode receives template flags
- **WHEN** existing-project mode is combined with project generation or profile
  rendering options
- **THEN** bootstrap fails before mutation and explains the mode boundary

### Requirement: Explicit README and Git initialization
Initial bootstrap MUST support separate opt-ins for a minimal README and Git
repository initialization. Git options MUST never stage, commit, push, create a
remote repository or publish external state.

#### Scenario: Empty consumer requests README
- **WHEN** an operator passes `--with-readme` for a new target
- **THEN** bootstrap renders a public-safe minimal project README

#### Scenario: Consumer requests Git initialization
- **WHEN** an operator passes `--init-git` with a default branch and optional
  remote
- **THEN** bootstrap initializes or confirms the requested local Git state
- **AND** leaves the worktree uncommitted and unpushed

#### Scenario: README or Git state conflicts
- **WHEN** an existing README, repository branch or remote contradicts requested
  initialization
- **THEN** bootstrap fails closed without overwriting or publishing state

#### Scenario: Git detail is supplied without opt-in
- **WHEN** a default branch or remote is supplied without `--init-git`
- **THEN** bootstrap rejects the combination before target mutation
