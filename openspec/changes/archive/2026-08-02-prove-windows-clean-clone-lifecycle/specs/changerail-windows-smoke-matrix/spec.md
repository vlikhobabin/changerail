## ADDED Requirements

### Requirement: Clean-clone Windows lifecycle proof
The Windows smoke matrix MUST include an explicit live clean-clone lifecycle
proof before ChangeRail claims full native Windows support.

#### Scenario: Live matrix runs clean-clone proof
- **WHEN** a maintainer runs `python3 scripts/smoke-windows-matrix.py --live`
- **THEN** the matrix runs a clean-clone lifecycle proof against
  `windows-host-a` and `windows-host-b`
- **AND** the proof starts each host from a disposable clone of the ChangeRail
  source ref under the ignored Windows lab root
- **AND** tracked summaries identify only generic host ids, command class,
  outcome and ignored runtime report paths

#### Scenario: Clean-clone proof exercises consumer lifecycle
- **WHEN** the clean-clone lifecycle proof runs on a host
- **THEN** it launches required native `.cmd` helpers from the cloned source
- **AND** it creates a generated-copy consumer project through
  `bootstrap-project.cmd`
- **AND** it runs `verify-project.cmd` against that consumer
- **AND** it confirms required ChangeRail skills, Claude commands and helper
  wiring are discoverable through project-local generated paths
- **AND** it refreshes generated wiring without modifying project-owned files
- **AND** it proves an explicit no-push staging fixture excludes ignored runtime
  files from the Git index

#### Scenario: Clean-clone proof cannot complete
- **WHEN** clone, bootstrap, verification, discovery, refresh or scoped staging
  fails on either host
- **THEN** the matrix reports the item as failed
- **AND** ChangeRail MUST record a sanitized blocker or caveat instead of
  claiming full native Windows support from that run
