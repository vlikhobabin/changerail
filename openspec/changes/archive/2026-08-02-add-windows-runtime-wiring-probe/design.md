## Context

`030-01` established a native Windows lab protocol and a sanitized two-host
support matrix. `030-02` now needs a deeper but still disposable probe that
observes runtime invocation, directory/file wiring and Git behavior on native
Windows before `030-03` selects an architecture.

The existing `scripts/windows-lab-probe.py` already owns inventory parsing,
generic host ids, ignored raw evidence and non-interactive SSH execution. The
new harness should reuse those rules, but the actual fixture must be purpose
built for symlink, junction, wrapper and Git checks.

## Goals / Non-Goals

**Goals:**
- Add a stdlib Python harness with `dry-run` and `run` modes.
- Execute all live checks inside per-run disposable roots from ignored
  inventory.
- Produce sanitized host summaries for direct directory symlink, file symlink,
  junction, wrapper launch variants, Git traversal and generated-copy drift.
- Retain raw host output only under ignored `.runtime/changerail/` paths.

**Non-Goals:**
- Choose the final native Windows architecture.
- Modify `bin/openspec`, `bin/bootstrap-project`, `bin/verify-project` or
  generated consumer templates.
- Request UAC, `runas`, administrator elevation or persistent machine
  configuration.

## Decisions

1. Create a separate probe script instead of extending `windows-lab-probe.py`.
   - Path: `scripts/windows-runtime-wiring-probe.py`.
   - Rationale: readiness probing and destructive-ish disposable Git/runtime
     experiments have different result schemas and failure semantics.
   - Alternative rejected: add many mode flags to `windows-lab-probe.py`; that
     would make the readiness harness harder to audit.

2. Build the remote fixture entirely in the disposable root.
   - The fixture contains a miniature ChangeRail-like source tree, consumer
     tree and Git repository.
   - Symlink/junction/generated-copy paths point only inside that disposable
     root.
   - Rationale: this reproduces wiring behavior without touching real
     ChangeRail or consumer worktrees.

3. Treat failed operations as observations when the host remains usable.
   - For example, direct `os.symlink` without Developer Mode may return
     `failed` or `not-applicable`, while the aggregate host result can still be
     usable if cleanup and reporting succeed.
   - Rationale: the card asks for reproduction and comparison, not for every
     strategy to pass.

4. Summarize trade-offs from observed check classes.
   - The harness emits stable strategy names and per-host outcomes.
   - Tracked docs convert those outcomes into security, portability, Git and
     operator trade-offs.
   - Rationale: `030-03` needs comparable evidence rather than raw command
     transcripts.

## Risks / Trade-offs

- [Risk] Windows quoting or PowerShell JSON conversion can hide the root
  failure. Mitigation: write raw stdout/stderr under ignored runtime evidence
  and include sanitized diagnostics in the JSON report.
- [Risk] Current SSH tokens are elevated on both hosts, so direct symlink checks
  may not prove non-elevated behavior. Mitigation: the host result records the
  token state and Developer Mode status; if non-elevated mode is unavailable,
  the strategy records an explicit evidence caveat.
- [Risk] Git behavior may vary by version. Mitigation: the host summary includes
  the Git version and records status/add traversal using porcelain and dry-run
  outputs, not console-only display.

## Migration Plan

1. Add the harness and local sample dry-run report.
2. Run the live probe through ignored inventory.
3. Use the results change to publish only sanitized conclusions.

## Open Questions

- The final architecture choice remains delegated to `030-03`.
