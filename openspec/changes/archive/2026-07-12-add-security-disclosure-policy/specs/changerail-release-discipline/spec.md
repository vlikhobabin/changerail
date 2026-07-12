## MODIFIED Requirements

### Requirement: Migration notes between versions
Release verification MUST include security disclosure policy and public-safety
checks for public ChangeRail releases.

#### Scenario: Release checks security disclosure policy
- **WHEN** a maintainer prepares a public ChangeRail release
- **THEN** release verification confirms that tracked security disclosure
  policy exists and is linked from public docs
- **AND** public-safety scans pass for the final tracked payload

## ADDED Requirements

### Requirement: Security disclosure policy
ChangeRail MUST maintain a tracked public security disclosure policy for
reporting vulnerabilities without publishing sensitive details.

#### Scenario: Public user reports a vulnerability
- **WHEN** a public user reads `SECURITY.md`
- **THEN** the policy identifies supported versions, preferred private
  disclosure channel and report content guidelines
- **AND** it tells reporters not to include secrets, credentials, exploit
  payloads or private workspace details in public issues
