## Context

`030-01` must prove that two native Windows hosts are usable for later
research. The probe must answer only baseline readiness questions:
SSH reachability, non-interactive command execution, safe fixture transfer,
disposable root setup and sanitized OS/filesystem/Git/Python/shell/privilege
capabilities.

The card is explicitly not the place to reproduce symlink, junction, Git staging
or extensionless-wrapper failures. Those probes are scoped to `030-02` after
the lab protocol and support matrix are published.

## Goals / Non-Goals

**Goals:**
- Execute the Windows lab harness against both ignored inventory hosts.
- Produce a sanitized matrix in tracked compatibility notes.
- Retain raw command output and generated reports in ignored runtime evidence.
- Record concrete verification commands and outcomes.

**Non-Goals:**
- Modify ChangeRail runtime, bootstrap scripts or consumer templates.
- Choose Windows architecture defaults.
- Execute destructive filesystem or Git wiring probes.

## Decisions

1. Publish a concise matrix in `docs/compatibility.md`.
   - Rationale: compatibility notes are the existing durable public surface for
     tool/platform support expectations.
   - Alternative rejected: committing generated raw JSON. Raw reports can carry
     machine-local paths or command output and belong under `.runtime/`.

2. Record capability values as sanitized status fields.
   - OS, filesystem, Git, Python, shell and privilege checks are recorded as
     present/version-like values or explicit unavailable/not-applicable status.
   - Raw hostnames, usernames, Windows profile paths and disposable root values
     are excluded.

3. Treat fixture transfer as SSH stdin content delivery.
   - The harness sends a small deterministic fixture over the existing SSH
     channel, writes it inside the disposable per-run directory and validates a
     hash on the host.
   - Rationale: this proves safe fixture transfer without requiring a separate
     `scp` command or storing credentials in repository files.

## Risks / Trade-offs

- [Risk] A host may have no `python` on PATH but still have `py -3`. Mitigation:
  the matrix records both command outcomes where available instead of collapsing
  them into a single unsupported result.
- [Risk] Filesystem type discovery may vary by Windows edition or permissions.
  Mitigation: unsupported discovery is recorded as `unknown` with a passing
  root setup/fixture check when the disposable workspace still works.
- [Risk] Live host evidence can become stale. Mitigation: the tracked matrix is
  labeled as the current `030-01` research baseline, and future architecture
  decisions must cite the retained evidence path or re-run the harness.

## Migration Plan

1. Run `scripts/windows-lab-probe.py run` with the ignored inventory.
2. Copy only sanitized matrix values and evidence path summaries into
   `docs/compatibility.md` and the board card.
3. Run OpenSpec validation, dry-run validation and public-surface scan.

## Open Questions

- Native Windows architecture defaults remain open until `030-03`.
