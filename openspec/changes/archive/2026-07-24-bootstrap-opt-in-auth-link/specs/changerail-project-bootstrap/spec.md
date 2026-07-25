## ADDED Requirements

### Requirement: Opt-in Codex auth symlink setup
Bootstrap MUST support an explicit operator opt-in for linking a generated
consumer's ignored Codex auth marker to an existing local auth file without
copying credentials.

#### Scenario: Default bootstrap does not link auth
- **WHEN** an operator runs `bin/bootstrap-project /opt/example-project --name
  example-project --kind generic` without an auth link option
- **THEN** bootstrap does not create `.codex/auth.json`
- **AND** generated `.gitignore` keeps `.codex/auth.json` ignored

#### Scenario: Operator links an existing auth file
- **WHEN** an operator runs bootstrap with `--link-codex-auth
  $HOME/.codex/auth.json`
- **THEN** bootstrap creates `/opt/example-project/.codex/auth.json` as a
  symlink to the supplied source
- **AND** bootstrap does not read or print credential contents

#### Scenario: Auth link source is missing
- **WHEN** an operator supplies `--link-codex-auth` with a missing source path
- **THEN** bootstrap exits non-zero before reporting success
- **AND** it does not create a dangling auth marker by default

#### Scenario: Dry-run reports auth link plan
- **WHEN** an operator runs bootstrap with `--dry-run --link-codex-auth
  $HOME/.codex/auth.json`
- **THEN** bootstrap prints a planned auth symlink operation
- **AND** it writes no target files
