## ADDED Requirements

### Requirement: Repository rename gate before known consumer migration
Known consumer migration MUST NOT start until the ChangeRail repository remote
has been updated after the GitHub repository rename.

#### Scenario: Repository remote still points to old OPSX URL
- **WHEN** delivery reaches known consumer migration and `git remote -v` still
  points at the old `opsx` repository URL
- **THEN** delivery stops before editing any consumer project
- **AND** it asks the operator to rename the GitHub repository to `changerail`
  and update or confirm local `origin`

#### Scenario: Repository remote points to ChangeRail URL
- **WHEN** delivery reaches known consumer migration and `git remote -v` points
  at the `changerail` repository URL
- **THEN** delivery may proceed to the one-project-at-a-time consumer migration
  protocol

### Requirement: Known consumer migration verification
Each known local consumer rewired by the operator MUST pass the post-rename
ChangeRail project verification gate before being treated as ChangeRail-wired.

#### Scenario: Consumer rewiring completes
- **WHEN** an operator finishes rewiring one selected consumer project
- **THEN** `/opt/changerail/bin/verify-project <project>` passes for that
  project
- **AND** the verification result is recorded in the consumer repository or
  ignored operator notes

#### Scenario: Active session cannot be stopped immediately
- **WHEN** a selected consumer cannot safely stop active Claude/Codex sessions
  during the main ChangeRail rename
- **THEN** the remaining restart and fresh-context verification work is tracked
  in a separate board card
- **AND** the consumer is not treated as ready for `/changerail:*` or
  `$changerail-*` use until that follow-up is complete

#### Scenario: Consumer has unrelated work in progress
- **WHEN** the selected consumer has unrelated dirty tracked files before
  migration
- **THEN** migration pauses for that project instead of mixing wiring changes
  with unrelated work
