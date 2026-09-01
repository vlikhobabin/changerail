## ADDED Requirements

### Requirement: First stable release metadata is coherent
ChangeRail `1.0.0` MUST publish one coherent metadata set whose version,
changelog, compatibility, migration and release notes agree on the stable
support boundary and transition from `0.5.0`.

#### Scenario: Consumer evaluates the stable upgrade
- **WHEN** a consumer reads the `1.0.0` release payload
- **THEN** root `VERSION` contains exactly `1.0.0`
- **AND** `CHANGELOG.md` contains dated `1.0.0` entries and a new empty
  `Unreleased` section
- **AND** compatibility and migration docs describe required actions,
  verification and rollback for `0.5.0 -> 1.0.0`
- **AND** metadata does not claim dependency-pin changes that did not occur

#### Scenario: Native Windows final proof is unavailable
- **WHEN** no current public-safe live native Windows evidence exists for the
  exact release candidate
- **THEN** release-facing docs state a reviewed Linux-focused stable support
  boundary
- **AND** they present native Windows as not release-certified rather than
  inventing or extrapolating host evidence

### Requirement: First stable candidate receives sequential isolated certification
The first stable ChangeRail candidate MUST complete its release verification
floor in an isolated clone of the exact frozen payload with pinned development
dependencies and no more than two CPUs available to heavy suites.

#### Scenario: Maintainer certifies the frozen candidate
- **WHEN** tracked release preparation is complete
- **THEN** the core and extended release suites run strictly sequentially in
  the same isolated candidate clone
- **AND** release CI smoke, current/history public scans and applicable trusted
  dependency integrity checks pass for that candidate
- **AND** evidence binds the outcomes to one exact commit/tree fingerprint

#### Scenario: Candidate check fails or changes
- **WHEN** a required check fails or tracked candidate bytes change after the
  recorded evidence
- **THEN** final certification fails closed
- **AND** the affected verification and fresh independent review are repeated
  before publication

### Requirement: First stable tag and public release are remotely verifiable
ChangeRail MUST publish `v1.0.0` as an annotated tag on the exact reviewed and
published release commit and MUST expose the contracted source assets through
a public GitHub Release.

#### Scenario: Release publication succeeds
- **WHEN** all final gates are green and the reviewed commit is reachable from
  the authorized remote branch
- **THEN** annotated tag `v1.0.0` dereferences to that exact commit
- **AND** the public GitHub Release targets the same tag
- **AND** its archive, checksum and release metadata assets match the tracked
  distribution contract
- **AND** remote refs and downloaded asset checksums are confirmed read-only
- **AND** the release card moves from `3.inprogress` to `4.done` only after
  those publication proofs succeed

#### Scenario: Reviewed working tree becomes the release commit
- **WHEN** canonical verdict freshness passed immediately before scoped staging
- **THEN** the payload commit parent equals the verdict's recorded HEAD
- **AND** the payload commit tree equals the verdict's recorded tree
- **AND** the clean committed state is not presented as another fresh verdict
  or used to require an undeclared clean-HEAD LLM audit

#### Scenario: First stable publication resumes after a partial upload
- **WHEN** `v1.0.0` uses exact annotation `ChangeRail 1.0.0` and the public
  release uses exact title `ChangeRail 1.0.0` and notes body from tracked
  `docs/releases/1.0.0.md`
- **THEN** every present uploaded asset has a unique contracted basename and
  byte-matches the fresh build from the tag
- **AND** only an absent contracted basename may be uploaded on resume
- **AND** a duplicate, unexpected or mismatched asset fails closed without
  replacement

#### Scenario: Publication authority or identity is unavailable
- **WHEN** tag/release credentials are unavailable or an existing object has
  unexpected target or metadata
- **THEN** publication stops at the exact safe handoff
- **AND** no force update, replacement tag or fabricated release evidence is
  used
- **AND** the release card remains `3.inprogress` until the transaction can be
  resumed and proved complete
