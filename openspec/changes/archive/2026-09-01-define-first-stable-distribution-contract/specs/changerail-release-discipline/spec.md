## ADDED Requirements

### Requirement: Reproducible generic source distribution
ChangeRail MUST publish a language-neutral source archive built from one exact
Git commit, and repeated builds from that commit with the same tracked builder
MUST produce byte-identical archive and metadata assets.

#### Scenario: Maintainer builds a release bundle
- **WHEN** a maintainer invokes the tracked source-distribution builder for an
  exact commit whose tree contains a valid `VERSION` and `LICENSE`
- **THEN** it produces a gzip-compressed tar archive under one
  `changerail-<version>/` root
- **AND** the archive contains only files tracked by that commit
- **AND** a repeated build from the same commit produces identical bytes

#### Scenario: Source ref or required metadata is invalid
- **WHEN** the source ref does not resolve to a commit or its tree lacks a
  valid semantic version or license file
- **THEN** the builder fails before claiming a release bundle
- **AND** it does not substitute working-tree or machine-local content

### Requirement: Source distribution identity and integrity metadata
Every ChangeRail source distribution MUST expose unambiguous version, license,
source-revision and SHA-256 metadata that can be verified without private or
machine-local state.

#### Scenario: Consumer verifies downloaded assets
- **WHEN** a consumer receives the archive, checksum sidecar and release
  metadata sidecar
- **THEN** the archive basename identifies the exact semantic version
- **AND** the checksum sidecar verifies the archive bytes
- **AND** release metadata names the dereferenced Git commit, `LICENSE`, archive
  basename and checksum basename
- **AND** the archive contains matching `VERSION` and `LICENSE` files

#### Scenario: Metadata does not match the candidate
- **WHEN** version, source revision, filename or checksum disagree with the
  exact release candidate
- **THEN** release publication fails closed
- **AND** no mismatched asset is described as the ChangeRail release

### Requirement: Reviewed release publication order
ChangeRail MUST create a release tag and public distribution only after a
fresh risk-appropriate review has approved the exact payload and the scoped
release commit is remotely reachable.

#### Scenario: Final review has not returned GO
- **WHEN** the semantic verdict is absent, stale, invalid or negative
- **THEN** the release commit is not published as a stable release
- **AND** no release tag or public distribution is created

#### Scenario: Existing publication identity is unexpected
- **WHEN** the intended tag or public release already exists with an
  unexpected target, annotation or asset metadata
- **THEN** publication stops without rewriting the existing identity
- **AND** force-push, tag replacement and destructive recovery are forbidden
