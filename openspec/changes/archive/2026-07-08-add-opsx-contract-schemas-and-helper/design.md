## Context

OPSX needs stable public wire ids before new consumers are bootstrapped. This
change introduces the `opsx.*` namespace and makes the review-verdict helper
validate the canonical public id.

## Goals / Non-Goals

**Goals:**
- Add JSON schemas with canonical `opsx.*` schema ids.
- Add a review-verdict helper that can validate verdict shape and freshness.
- Keep helper output deterministic and dependency-light.
- Document canonical helper usage.

**Non-Goals:**
- Add a delivery-manifest normalization helper.
- Add an evidence bundle builder.
- Persist runtime verdicts or manifests in git.

## Decisions

1. Canonical schema ids are:
   - `opsx.review-verdict.v1`
   - `opsx.delivery-manifest.v1`
   - `opsx.evidence-index.v1`
2. `scripts/opsx_review_verdict.py validate` accepts only
   `opsx.review-verdict.v1` and reports that schema id in successful output.
3. Freshness is based on `git rev-parse HEAD`, `git status --porcelain` and
   `git diff HEAD --no-color`, hashed as a deterministic `sha256:<hex>` value.
4. `bin/opsx-review-verdict` is a thin Python launcher that resolves the helper
   relative to `/opt/opsx` or to the consumer path used to invoke a symlink.

## Risks / Trade-offs

- JSON Schema alone cannot enforce every cross-field review invariant.
  Mitigation: the helper performs additional consistency checks, including
  blocker/no-go consistency.
- Non-canonical contract ids can hide migration drift. Mitigation: helper
  validation accepts only the canonical OPSX schema id.
