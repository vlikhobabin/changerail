## Context

Published authorization v13 is the latest safe executable boundary. Its clean
implementation successor remained unpublished after cycle 1 `9/14`, one
bounded repair and terminal cycle 2 `9/14`: exact descriptor identity,
dangling-symlink admission, independently complete source-bound scheduler
mutants and public R/C selection remained open. Because those classes repeat
older affected-profile boundaries, another implementation patch is forbidden
until a clean docs-only decision is published.

## Goals / Non-Goals

**Goals:**

- Turn every cycle-2 blocker into a finite public-boundary contract with an
  independent normative oracle.
- Separate target identity from mere target usability.
- Make non-following filesystem inspection precede existence branching.
- Make scheduler completeness include source/AST mutation and guard-order
  reachability for every valid reason tuple.
- Make rename/copy proof cover exact grammar and both old/new operands through
  all three diff streams.
- Freeze one bounded v14 authorization and implementation path.

**Non-Goals:**

- No executable v14 card, test, source, CI or dependency work.
- No repair, reproduction or inspection of terminal v13 tracked/runtime payload.
- No history, full/affected execution, benchmark, live matrix or certification.
- No new receipt, evidence, authority or wire protocol.

## Decisions

### 1. Descriptor identity has an independent closed source

Future production task descriptors and actual source/AST command tokens will
be compared bidirectionally with a separately authored immutable descriptor
map. A probe proves usability only after its exact token, kind and target
identity match the map. This prevents a different usable OpenSpec executable or
repository target from satisfying the intended guard. Deriving the oracle from
the production task table was rejected because consistent drift would pass.

### 2. Runtime admission uses non-following inspection first

Every ancestor, parent and leaf is classified with `lstat` or an equivalent
non-following primitive before any `exists()`-style branch. A dangling symlink
is therefore an existing invalid directory entry, not a missing admissible
leaf. Resolution and access checks remain additive after lexical type checks.
Following-only `resolve()`/`exists()` logic was rejected because broken links
collapse into the missing-leaf path.

### 3. Scheduler requirements and executable mutants are separate axes

The normative map enumerates every valid reason tuple and top-level invariant.
A distinct mutant map binds each row to its own passing canonical neighbor,
one-field data mutation, exact production source/AST guard mutation and public
observation. Guard-order sentinels prove all preceding admission/validation
branches passed, so an early failure cannot mask a disconnected mutant.
Generating all invalid rows from `completed` was rejected because cross-field
guards for terminal, outer, synthetic and cancelled rows remain unobserved.

### 4. Selector proof is stream × grammar × operand complete

Committed, staged and unstaged name-status streams each receive valid A/M/D and
valid R/C score-boundary cases plus invalid score width/range/sign/case,
framing and missing-operand cases. Valid rename/copy cases independently assert
that both old and new paths affect selection. Untracked remains a separate
NUL-path grammar. Private parser assertions remain useful diagnostics but
cannot satisfy public fallback acceptance.

### 5. V14 remains a clean bounded successor

This decision owns the exact six-field investigation authorization object with
a 500-line ceiling, while the future implementation card is stricter at 499
production LOC. Authorization v14 will be a separate docs-only reviewed and
published card. The implementation must reconstruct from published sources;
terminal v13 contributes only validated chronology and finding classes.

## Risks / Trade-offs

- **[Risk] The finite catalog becomes large.** → Require stable guard IDs,
  bidirectional map equality and one public observation per row; size alone is
  not evidence of completeness.
- **[Risk] Source mutants become coupled to formatting.** → Bind semantic AST
  shapes where possible and retain literal-source mutants only for exact token
  contracts.
- **[Risk] Strict descriptor identity rejects a valid local substitute.** →
  This is intentional for release authority; changing a frozen tool is a new
  reviewed contract, not runtime recovery.
- **[Trade-off] Full fallback remains slower on uncertainty.** → Affected mode
  is feedback-only, so preserving coverage dominates narrow speed.

## Migration Plan

1. Publish this docs-only investigation from authorization v13 HEAD.
2. Publish a separate docs-only authorization v14 containing the exact object
   and dependencies frozen here.
3. Build one clean v14 implementation from that authorization without reading
   terminal v13 material.
4. Run allowed focused/static/current checks and one fresh ordinary/high review.
5. Only after published implementation may final critical certification run.

Rollback discards this docs-only branch before publication; after publication,
authorization v13 remains the latest safe dormant executable reference until a
reviewed v14 implementation is remotely reachable.

## Open Questions

None. The unresolved guard classes and exclusive successor order are fixed by
the terminal verdict summary and accumulated published contract.
