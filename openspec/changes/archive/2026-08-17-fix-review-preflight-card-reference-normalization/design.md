## Context

Authorization validation extracts backticked relation values and compares them
directly to a card id. Existing published cards use `<id>.md`, which is an
equivalent board-card reference but fails that literal comparison.

## Goals / Non-Goals

**Goals:**
- Normalize only the three documented exact forms to their card id.
- Reject path traversal, a different filename stem, a non-board path and
  references with extra suffixes.

**Non-Goals:**
- Infer cards from arbitrary prose, permit fuzzy matching or change authority
  source semantics.

## Decisions

1. Normalize each full backticked reference, then compare exact ids.

   A bare id is retained. A filename is accepted only when its sole suffix is
   `.md`; a path is accepted only below `openspec/board/` with a recognized
   board lane and an `<id>.md` final component. Every other value produces no
   candidate, so `expected in candidates` remains fail-closed.

2. Keep normalization in the existing matcher.

   The published-investigation path is the only consumer, and a helper would
   add surface without reducing complexity.

## Risks / Trade-offs

- A permissive path parser could authorize an unrelated card -> require the
  canonical board root/lane and exact final stem.
- Existing prose may contain valid-looking text -> only complete backticked
  values from the declared heading are considered.
