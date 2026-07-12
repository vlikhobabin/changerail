## Context

The repository has public-safety rules in `AGENTS.md` and methodology docs, but
no durable public-facing vulnerability reporting policy. A reporter should not
need to infer where to send credentials, supply-chain concerns or runtime data
leak reports.

## Goals / Non-Goals

**Goals:**
- Provide supported versions guidance.
- Provide a private disclosure channel using repository-hosted private
  vulnerability reporting when available.
- Tell reporters not to include secrets or exploit details in public issues.
- Link the policy from public docs.

**Non-Goals:**
- Do not invent a private email alias that the project does not operate.
- Do not add paid security program terms or SLA promises.
- Do not commit vulnerability reports or local traces.

## Decisions

- Use `SECURITY.md` as the canonical public policy file.
- Name GitHub private vulnerability reporting / Security Advisories as the
  preferred private channel, with a minimal public issue fallback that asks for
  a maintainer-provided private channel without sensitive details.
- Add release discipline wording that security policy presence and public
  safety scans are part of release verification.

## Risks / Trade-offs

- [Risk] A public fallback issue may be misused to include secrets. Mitigation:
  policy explicitly says public fallback issues must contain only a minimal
  contact request and no sensitive payload.
