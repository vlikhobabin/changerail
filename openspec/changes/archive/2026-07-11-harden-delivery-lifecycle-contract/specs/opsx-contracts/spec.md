## ADDED Requirements

### Requirement: Delivery manifest file operations
Delivery manifests MUST represent card-owned file operations well enough for
publish to build a complete staging proposal for additions, modifications,
deletions and renames.

#### Scenario: Board card move is claimed completely
- **WHEN** a card moves from one board column path to another
- **THEN** the manifest records the source path and target path or equivalent
  structured operation data so publish can stage both sides of the move

#### Scenario: Deleted path remains in scope
- **WHEN** delivery removes a card-owned tracked file
- **THEN** the manifest records the deleted path as a committable path instead
  of only recording remaining files
