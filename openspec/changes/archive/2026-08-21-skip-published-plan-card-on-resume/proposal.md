# Proposal: skip published plan card on resume

## Why
An aggregate run can stop on a card, while a scoped rescue later publishes that
same card. The next `resume-plan` re-resolves the path to `4.done` but currently
relaunches the delivery child because the retained aggregate state is still
blocked. A compliant child may then refuse the already-published request, which
creates a false safety stop before downstream cards.

## What Changes
- Reconcile a current, safely published card before dispatch during push-mode
  resume.
- Reuse the existing queue success proof: one `4.done` location, clean tree and
  `HEAD == upstream`.
- Retain fail-closed behavior when any part of that proof is absent.

## Capabilities
- `changerail-delivery-runner`
