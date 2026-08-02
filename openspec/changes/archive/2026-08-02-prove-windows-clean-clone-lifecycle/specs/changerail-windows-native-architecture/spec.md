## ADDED Requirements

### Requirement: Final clean-clone support proof
The native Windows implementation MUST pass an end-to-end clean-clone proof on
both Windows lab hosts, or record an explicit support blocker, before the
architecture decision is presented as implemented support.

#### Scenario: Maintainer reads final support evidence
- **WHEN** native Windows implementation is claimed as supported
- **THEN** tracked docs cite a retained ignored clean-clone lifecycle report
- **AND** the report covers both `windows-host-a` and `windows-host-b`
- **AND** the report includes generated-copy bootstrap, verification, discovery,
  refresh/update and scoped no-push staging outcomes

#### Scenario: Support proof has a blocker
- **WHEN** either Windows host cannot complete the clean-clone lifecycle proof
- **THEN** ChangeRail records the blocker or caveat with sanitized evidence
- **AND** docs do not present the blocked path as full native Windows support
