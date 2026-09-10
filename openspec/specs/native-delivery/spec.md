# Native delivery

## Purpose

Define the portable delivery and project isolation contract for the current
ChangeRail runtime, preserving evidence and review accounting across continuations.

## Requirements

### Requirement: Native lifecycle
The runtime SHALL execute one openspec-v1 change per card and SHALL allow at most
two independent review cycles across ordinary delivery and repair.

#### Scenario: Repair accounting
- **WHEN** a run resumes or performs a semantic repair
- **THEN** previous independent reviews remain counted
- **AND** historical allowances do not create another review cycle

### Requirement: Separate project and tool ownership
The runtime SHALL keep project Git operations, profile, board and evidence in
the selected project while loading shared code from its declared tool source.

#### Scenario: Shared source
- **WHEN** two projects are attached to one source checkout
- **THEN** each observes the same shared code
- **AND** each retains its own profile, delivery lock and runtime artifacts

### Requirement: Explicit source change
The runtime SHALL retain the effective code identity for execution and SHALL
refuse ordinary continuation when the frozen identity changes.

#### Scenario: Repair continuation
- **WHEN** a stopped eligible run adopts a tested tool correction
- **THEN** a separate receipt records previous and new identity and regression evidence
- **AND** the original run metadata and consumed reviews remain unchanged

#### Scenario: Shared OpenSpec runtime drift
- **WHEN** an OpenSpec workflow loader, installation checker, package manifest,
  package lock, bootstrap or shared Python package initializer changes
- **THEN** ordinary continuation refuses the changed execution identity
- **AND** linked consumers enforce the same check without rewriting saved runs

### Requirement: Recover interrupted source attachment
The installer SHALL require ignored runtime storage before attaching shared
source and SHALL permit detachment from an unavailable source using checked
local backups without granting execution authority to broken links.

#### Scenario: Source moved after attachment
- **WHEN** the shared checkout is moved or removed and the attachment links and
  retained local backup are unchanged
- **THEN** detach restores the exact pre-attachment files
- **AND** normal runtime execution still rejects the unavailable source

#### Scenario: Attachment without ignored runtime storage
- **WHEN** attachment is requested without ignored runtime storage
- **THEN** the installer refuses before writing lock, backup or attachment files

### Requirement: Preserve archive intent through date rollover
The runtime SHALL preserve the initial archive intent while allowing its UTC
destination date to advance through linked receipts after revalidating the exact
payload, HEAD and absence of conflicting archive destinations.

#### Scenario: Stopped before stock archive
- **WHEN** a saved intent predates the current UTC date and the active change
  still matches its retained artifacts and surrounding payload
- **THEN** the runtime records a successor intent before invoking stock archive
- **AND** continuation preserves the original intent and successor chain

### Requirement: History remains read only
The runtime SHALL preserve historical adopted runs without granting new execution authority.

#### Scenario: Read old run
- **WHEN** status or metrics reads an adopted run
- **THEN** its saved files remain unchanged
- **AND** observation does not authorize resume or publication
