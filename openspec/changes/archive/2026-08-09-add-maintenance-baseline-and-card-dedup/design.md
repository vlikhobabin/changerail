## Context

The previous lifecycle change adds normalized findings with stable identity and
ignored runtime state. This change adds the durable tracked control plane around
those findings: baseline acceptance, temporary waivers, schema-bound triage
annotations and a preview/write bridge to ChangeRail board cards.

The bridge must be generic ChangeRail core behavior. It cannot call an LLM,
cannot write by default and cannot expose raw detector output, absolute
consumer paths or private snippets in tracked cards.

## Goals / Non-Goals

**Goals:**
- Publish `.changerail/maintenance-baseline.yaml` schema semantics with
  separate `accepted` and `waivers` collections.
- Add fail-open expired waiver handling.
- Add preview-first CLI commands: `accept-baseline`, `triage` and `cards`.
- Upsert board cards by exact `Maintenance Origin: <sha256 fingerprint>`
  marker across all board lanes.
- Keep card content sanitized and repository-relative.

**Non-Goals:**
- No LLM-powered triage.
- No automatic card writes from `scan` or `report`.
- No mutation of raw detector schemas from `060-02`.
- No domain-specific detector adapters.

## Decisions

1. Baseline lives at `.changerail/maintenance-baseline.yaml` and is tracked
   only when maintainers opt in. Alternative: store baseline under runtime
   state; rejected because acceptance and waivers must be reviewable in Git.
2. `accept-baseline` emits a preview by default and writes only with `--write`.
   The command takes normalized lifecycle report input or runs `report`
   implicitly when no input path is supplied.
3. `triage` validates schema-bound annotations and returns normalized JSON; it
   never invokes an LLM. Agents can produce annotations, but CLI validates only
   the contract.
4. `cards` emits preview card artifacts below
   `.runtime/changerail/maintenance/previews/` by default. With `--write`, it
   scans `openspec/board/1.backlog` through `5.canceled` for the exact origin
   marker and updates the matching existing card, otherwise creates a backlog
   card.
5. Card content uses lifecycle finding fields only: fingerprint, detector, rule,
   severity, path, risk class, remediation and sanitized evidence refs. Raw
   detector evidence remains indirect runtime evidence.

## Risks / Trade-offs

- [Risk] Suppression can hide active risk. → Mitigation: acceptance is keyed by
  identity and waiver requires owner, reason and expiry/review boundary; expired
  waiver does not suppress open findings.
- [Risk] Duplicate cards can still appear if a human removes the marker. →
  Mitigation: exact marker is mandatory on write and smoke tests cover all board
  lanes.
- [Risk] Preview artifacts could be mistaken for tracked payload. → Mitigation:
  previews stay under ignored `.runtime/changerail/maintenance/previews/` and
  CLI output includes target paths.

## Migration Plan

No existing repository must create a baseline file. Maintainers can preview:

```bash
bin/changerail-maintenance accept-baseline --json
bin/changerail-maintenance cards --json
```

Tracked mutation requires:

```bash
bin/changerail-maintenance accept-baseline --write
bin/changerail-maintenance cards --write
```

Rollback removes the new optional commands and tracked baseline file without
changing scan/report contracts.

## Open Questions

- none
