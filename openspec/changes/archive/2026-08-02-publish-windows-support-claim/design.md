## Context

The final `040-05` card is the release-facing point where native Windows moves
from implemented pieces to a documented support claim. The docs currently
contain lab readiness, runtime/wiring reproduction, architecture decision and
automated smoke matrix notes, but they must be refreshed from final clean-clone
evidence before claiming support.

## Goals / Non-Goals

**Goals:**
- Publish a compatibility matrix that cites retained sanitized clean-clone,
  live matrix and Linux baseline evidence.
- Update migration/adoption guidance for native Windows operators using `.cmd`
  helpers and generated-copy default wiring.
- Document blocker/caveat semantics and refresh/update commands.
- Keep private Windows inventory, hostnames, usernames, credentials, raw output
  and machine-local paths out of tracked files.

**Non-Goals:**
- Do not change ChangeRail version or create a release tag in this card.
- Do not promise permanent Windows CI; future secure CI inventory remains a
  documented boundary.
- Do not document symlink/junction fallback as the default native Windows path.

## Decisions

1. Docs cite evidence by retained ignored path and concise outcome.
   - Rationale: reviewers need reproducible proof, but public docs must not
     embed raw lab output.

2. Compatibility docs become the support claim source.
   - Rationale: `docs/compatibility.md` already owns tool support status and
     current Windows lab sections.

3. Migration/adoption docs focus on consumer action.
   - Rationale: native Windows consumers need concrete commands:
     `.cmd` helpers, generated-copy refresh, `verify-project.cmd`, and
     caveat handling.

## Risks / Trade-offs

- [Risk] Docs over-claim least-privilege behavior if lab sessions remain
  elevated. -> Mitigation: docs distinguish generated-copy default from
  symlink/junction fallback and include caveats exactly as evidence supports.
- [Risk] Public-surface scan misses a private path. -> Mitigation: run current
  and history scans before publish, and keep evidence details concise.
