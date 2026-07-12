## MODIFIED Requirements

### Requirement: Delivery manifest derivation helper
Delivery manifest derivation MUST sanitize repository identity before writing it
to runtime records.

#### Scenario: Manifest redacts credential-bearing repository identity
- **WHEN** delivery manifest derivation reads an HTTPS remote containing URL
  userinfo, password or token-like query values
- **THEN** the manifest repository identity excludes raw userinfo, password,
  query and fragment values
- **AND** the identity retains non-sensitive scheme, host and repository path
  metadata when available

#### Scenario: Manifest redacts SCP-style SSH userinfo
- **WHEN** delivery manifest derivation reads an SCP-style SSH remote such as
  `user@example.invalid:org/repo.git`
- **THEN** the manifest repository identity excludes the raw SSH username
- **AND** it retains non-sensitive host and repository path metadata
