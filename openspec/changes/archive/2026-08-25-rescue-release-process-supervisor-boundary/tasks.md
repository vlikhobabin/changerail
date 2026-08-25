## 1. Decision artifacts

- [x] 1.1 Record the docs-only rescue card with future supersession, forensic
  boundary and review classification.
- [x] 1.2 Define the exact S/H4/I3/W1/R3/A3 order, ownership and six-field
  authorization objects in proposal, design and release-CI delta.

## 2. Contract synchronization

- [x] 2.1 Synchronize the modified release-CI requirement without rewriting
  historical cards, archives or old H/I authorization sources.
- [x] 2.2 Archive the same-slug decision change and keep the review-gated card
  in `3.inprogress` for independent handoff.

## 3. Verification

- [x] 3.1 Run `bin/openspec validate rescue-release-process-supervisor-boundary --strict`.
- [x] 3.2 Run `bin/openspec validate changerail-release-ci --strict` and
  `bin/openspec validate --all --strict`.
- [x] 3.3 Run deterministic exact-object/order/scope, JSON/TOML, current public
  scan, source classification and whitespace checks.
- [x] 3.4 Run review preflight for the docs-only handoff; RED evidence is not
  applicable because this change adds no executable behavior.

## 4. Cycle-1 ownership repair

- [x] 4.1 Move all canonical baseline/CI policy and oracle ownership from I3 to
  A3, add pre-A3 structural dormancy, and retain the existing ignored
  review verdict/history unchanged.
