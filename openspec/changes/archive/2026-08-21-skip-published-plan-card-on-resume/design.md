# Design: skip published plan card on resume

## Decision
During aggregate resume initialization, inspect the re-resolved current card
before considering its retained state. In push mode only, when the card is
published, call the existing `queue_success_check`. Mark it `skipped` with
result `DELIVERED` only when that complete check passes.

## Why pre-dispatch
The repository already contains stronger evidence than a child can add: the
card is uniquely in `4.done`, the tree is clean and the published branch equals
its upstream. Avoiding the child also avoids asking a lifecycle command to
deliver an already-finished card.

## Safety
- No success is inferred from the board path alone.
- No behavior changes for ordinary pending cards or `--no-push` resume.
- Dirty, ambiguous or non-equal upstream state follows the existing fail-closed
  path.
