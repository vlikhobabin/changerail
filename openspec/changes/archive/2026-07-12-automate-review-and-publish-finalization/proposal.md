# automate-review-and-publish-finalization

## Why

Fresh-review orchestration and post-publish card finalization are required by
the workflow, but the last delivery required manual reviewer prompt construction
and manual card-only amend steps.

## What Changes

- Strengthen `changerail-deliver` with a ready-to-run fresh reviewer prompt and
  validation sequence.
- Strengthen `changerail-pub` with deterministic card finalization and manifest
  publish-update helper guidance.
- Add helper support where practical for card finalization and manifest publish
  updates.

## Impact

- Affects lifecycle skills and delivery manifest helper.
- Updates `changerail-skill-surface` and `changerail-agent-methodology`
  specifications.
