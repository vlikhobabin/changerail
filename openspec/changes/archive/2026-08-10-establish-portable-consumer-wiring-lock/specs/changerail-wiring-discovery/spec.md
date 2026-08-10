## ADDED Requirements

### Requirement: Lock-aware POSIX wiring discovery
Wiring discovery MUST classify POSIX symlink backend, absolute/relative path
mode, consumer-lock state and source match without exposing resolved machine
paths in tracked or public output.

#### Scenario: Absolute locked consumer is inspected
- **WHEN** discovery inspects a valid absolute POSIX consumer lock
- **THEN** it reports backend `symlink`, path mode `absolute`, lock enforcement
  and source-match status
- **AND** public output does not include the resolved root

#### Scenario: Relative locked consumer is inspected
- **WHEN** discovery inspects an explicitly relative consumer
- **THEN** it reports path mode `relative` and the required shared-tree topology

#### Scenario: Lock and actual wiring disagree
- **WHEN** actual symlink targets contradict declared path mode or artifact intent
- **THEN** discovery reports broken wiring rather than normal source drift

### Requirement: POSIX clean-clone discovery evidence
ChangeRail MUST provide a regression fixture that commits a POSIX consumer,
clones it into a non-sibling path, performs lock-driven repair when needed and
then runs discovery and verification.

#### Scenario: Consumer checkout topology changes
- **WHEN** the clean-clone fixture moves only the consumer checkout
- **THEN** the documented absolute contract or lock-driven repair restores valid
  discovery without manual symlink edits
