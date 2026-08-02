## ADDED Requirements

### Requirement: Final native Windows support claim
ChangeRail MUST publish a final native Windows support claim only from retained
sanitized evidence that covers both Windows hosts or records explicit blockers.

#### Scenario: Compatibility matrix claims support
- **WHEN** a maintainer reads the native Windows compatibility section
- **THEN** it cites retained ignored evidence for the final clean-clone
  lifecycle proof
- **AND** it cites the aggregate live Windows smoke matrix outcome
- **AND** it identifies whether `windows-host-a` and `windows-host-b` passed or
  have explicit blockers
- **AND** it excludes raw hostnames, usernames, private Windows paths,
  credentials and SSH command strings

#### Scenario: Support claim includes caveats
- **WHEN** retained evidence has a host blocker, least-privilege caveat or
  unavailable dependency
- **THEN** the tracked support matrix records the sanitized caveat
- **AND** docs do not claim support for the blocked behavior

#### Scenario: Migration guidance follows support claim
- **WHEN** a native Windows operator reads migration or adoption guidance
- **THEN** it names `.cmd` helper entrypoints and generated-copy default wiring
- **AND** it identifies `verify-project.cmd` and refresh commands needed after
  ChangeRail updates
