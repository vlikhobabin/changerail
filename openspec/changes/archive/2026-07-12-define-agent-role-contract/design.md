## Context

The two-agent guide describes practical orchestration, but reusable agent
instructions need enough role guidance to be binding in consumer projects.

## Decisions

- Keep the role contract in `AGENTS.shared.md` so bootstrap embeds it into
  consumers.
- Reflect the same role names in `changerail-deliver`, `changerail-do` and
  `changerail-review`.
- Do not require a separate delivery worker for every small card. The hard
  boundary is independent review.

## Verification

- Validate the change and all specs.
- Run `git diff --check`.
- Scan touched skill/methodology docs for private paths.
