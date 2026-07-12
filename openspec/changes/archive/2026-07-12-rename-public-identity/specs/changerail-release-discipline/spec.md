## ADDED Requirements

### Requirement: Product rename migration notes
ChangeRail release discipline MUST treat the OPSX to ChangeRail rename as a
breaking migration for consumers.

#### Scenario: Consumer reads rename release notes
- **WHEN** a consumer reads the release notes for the rename version
- **THEN** the notes mark source path, command namespace, skill namespace,
  helper and schema namespace changes as breaking where applicable
- **AND** the notes describe `/opt/changerail` as the canonical source-of-truth
  path

#### Scenario: Operator renames the GitHub repository
- **WHEN** the GitHub repository is renamed from `opsx` to `changerail`
- **THEN** migration docs describe updating local `origin` to the new
  repository URL
- **AND** old repository URLs are treated as compatibility redirects, not
  canonical documentation targets
