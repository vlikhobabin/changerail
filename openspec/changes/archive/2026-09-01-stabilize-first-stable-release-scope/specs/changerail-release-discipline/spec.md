## ADDED Requirements

### Requirement: First stable release candidate has an explicit clean core scope
ChangeRail MUST build the first stable release candidate from the exact
published generic core reference and MUST exclude dirty, forensic, rejected or
explicitly deferred payloads unless each additional payload completes its own
scoped delivery, verification and independent review before release metadata is
prepared.

#### Scenario: Maintainer prepares the first stable release candidate
- **WHEN** a maintainer starts preparation of the first stable ChangeRail
  release
- **THEN** the candidate starts from the exact published `origin/main`
  reference
- **AND** local branch or worktree existence does not admit a payload into the
  candidate
- **AND** phase-routed delivery and runtime artifact retention remain outside
  the candidate while their board cards are explicitly deferred
- **AND** core and extended release suites complete sequentially in an isolated
  clone containing only release-reachable refs before version, tag or
  distribution publication

#### Scenario: Deferred or forensic work appears locally
- **WHEN** the release workspace can observe dirty, forensic, rejected or
  deferred work outside the candidate branch
- **THEN** that work MUST NOT be merged, staged, described as released or used
  as verification evidence solely because it exists locally
- **AND** machine-specific inventory remains ignored runtime evidence
- **AND** any later inclusion requires a separate scoped card, verification and
  fresh review

#### Scenario: Linked worktree shares unrelated local refs
- **WHEN** an implementation worktree shares a Git directory with forensic,
  rejected or deferred local refs
- **THEN** it is not used as the final reachable-history proof
- **AND** the exact candidate filesystem is verified in an isolated clone whose
  refs are limited to the release candidate lineage
- **AND** current-file scans still inspect the exact candidate payload while
  history scans inspect every commit reachable from the future release ref

#### Scenario: Stable release metadata work begins
- **WHEN** the clean core candidate has green core and extended suites and
  deferred work is absent from its tracked payload
- **THEN** version, changelog, compatibility, migration, tag and distribution
  metadata are prepared by a separate final-certification release card
- **AND** a scope-normalization card does not itself authorize release
  publication
