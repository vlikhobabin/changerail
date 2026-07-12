## Context

The board guide is now more specific than the root board README and consumer
board template. The root README also had stale wording from the pre-delivery
surface stage.

## Decisions

- Treat this change as docs/templates-only.
- Do not duplicate the whole guide into every consumer template; add concise
  board rules and a canonical pointer to the guide/shared methodology.
- Keep template examples generic and rendered through existing bootstrap
  placeholders.

## Verification

- Validate the change and all specs.
- Run `git diff --check`.
- Run a public-surface scan over touched docs/templates for private local
  paths and known consumer names.
