## Context

ChangeRail review currently consumes card prose, archived tasks, synced specs and
delivery manifests. The repository already defines `changerail.evidence-index.v1`,
but the schema is only a loose inventory and there is no helper that captures
verification command output with a common safety contract.

The card scope is limited to ChangeRail-owned verification commands. The helper
must not become a universal command recorder for secret-bearing or arbitrary
operator commands, and retained raw output must remain ignored runtime state.

## Goals / Non-Goals

**Goals:**
- Record command identity, timestamps, exit code, concise observed summary and
  raw output reference for verification checks.
- Keep raw output and indexes under `.runtime/changerail/`.
- Fail closed or redact when token-like arguments or output would be retained.
- Let manifests and review verdicts reference evidence IDs/paths without
  embedding raw logs.
- Cover success, failure, timeout, redaction and missing evidence with focused
  smokes.

**Non-Goals:**
- Recording every shell command an agent runs.
- Capturing interactive commands, arbitrary environment variables or screenshots.
- Committing raw logs, local runtime state or secret-bearing diagnostics.

## Decisions

1. Add a dedicated `changerail_evidence.py` helper and a `bin/changerail-evidence`
   entrypoint through the shared Python runtime selector.

   Rationale: retained evidence is a public ChangeRail contract and should use
   the same runtime selection and schema validation pattern as manifest and
   verdict helpers. A shell wrapper would make JSON/schema behavior harder to
   keep consistent.

2. Capture commands through explicit argv arrays.

   Rationale: argv input avoids shell parsing ambiguity, keeps command identity
   machine-readable and matches the card's implementation notes. Operators that
   need shell behavior can wrap it explicitly through a reviewed ChangeRail-owned
   smoke command.

3. Store runtime evidence under `.runtime/changerail/evidence/<scope>/`.

   Rationale: the location is already ignored by repository policy and keeps
   raw output separate from tracked specs, cards and schemas. Index entries use
   repository-relative paths so manifests and verdicts can reference them
   without machine-local absolute paths.

4. Treat secret-like argv values as a pre-execution blocker and redact
   secret-like output before writing retained output files.

   Rationale: refusing secret-like argv prevents intentional secret capture in
   process metadata. Output redaction keeps common accidental `token=value` style
   diagnostics out of retained raw files while preserving enough evidence for a
   reviewer to see that redaction occurred.

5. Extend manifest and verdict schemas with optional evidence references.

   Rationale: manifest/verdict files need stable links to evidence but must not
   embed logs. Optional references preserve backward compatibility for existing
   payloads and allow helper-backed validation where evidence is available.

## Risks / Trade-offs

- [Risk] Secret detection can miss unusual secret formats or flag harmless
  examples. -> Mitigation: keep the detector intentionally narrow, document it
  as a safety screen rather than a proof, and fail closed for obvious argv
  assignments.
- [Risk] Redacted output is not byte-for-byte command output. -> Mitigation:
  mark entries with `redacted: true` and diagnostics so reviewers know retained
  output was sanitized.
- [Risk] Evidence references can become stale if runtime files are deleted. ->
  Mitigation: provide a `validate` command and a missing-evidence smoke that
  fails closed for referenced runtime evidence paths.

## Migration Plan

1. Add schema fields and helper commands without changing existing manifest or
   verdict required fields.
2. Add focused smoke coverage and wire it into the release baseline.
3. Update delivery/review docs and skills to name retained evidence references
   as the preferred backing for verification command output.

No persistent migration is required for old runtime evidence; old manifests and
verdicts remain valid when they do not use evidence references.

## Open Questions

- none
