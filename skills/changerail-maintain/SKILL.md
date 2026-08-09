---
name: changerail-maintain
description: "Audit or triage ChangeRail repository maintenance findings without delivery, publish or fix mutation."
---

# ChangeRail Maintain

## Purpose

Consume deterministic repository maintenance output through an agent-facing
workflow:

```text
$changerail-maintain audit [--report <path>]
$changerail-maintain triage [--report <path>] [--annotations <path>] [--write-cards]
```

`changerail-maintain` is not a delivery, publish or fix workflow. It can explain
maintenance findings, validate operator-supplied triage annotations and prepare
preview artifacts, but tracked repository mutation stays behind explicit
operator intent and normal ChangeRail card delivery.

## Project Context

Resolve the repository root from the current working directory or
`CODEX_WORKDIR`. Read:

1. `openspec/config.yaml` if present.
2. `AGENTS.md`, `AGENTS.shared.md`, board docs and local workflow docs that
   affect public safety, repository boundaries or maintenance policy.
3. `.changerail/maintenance.yaml` and `.changerail/knowledge.yaml` when present.
4. The supplied maintenance report, annotations or preview path when provided.

Treat ignored runtime state under `.runtime/changerail/maintenance/` as evidence
only. Never commit runtime reports, annotations, previews, locks or raw logs.

## Inputs

Expected forms:

```text
$changerail-maintain audit
$changerail-maintain audit --report .runtime/changerail/maintenance/report.json
$changerail-maintain triage --report <path>
$changerail-maintain triage --annotations <path>
$changerail-maintain triage --write-cards
```

Accept legacy prompt forms such as `/changerail:maintain` and
`changerail:maintain` as equivalent, but present Codex CLI instructions with
`$changerail-maintain`.

If no mode is supplied, default to `audit`. If the user asks for `fix`, explain
that fix mode is not available until the separate scoped maintenance fix
workflow is delivered, then route the work to a normal ChangeRail board card and
`$changerail-deliver` handoff.

## Audit Mode

Audit is read-only.

1. If `--report <path>` is supplied, validate and inspect that report.
2. Otherwise run deterministic maintenance commands, preferring lifecycle
   report output:
   ```bash
   bin/changerail-maintenance report --json
   ```
   If lifecycle reporting is unavailable, fall back to:
   ```bash
   bin/changerail-maintenance scan --json
   ```
3. Explain open, waived, accepted or ambiguous findings in concise prose.
4. Report invalid, incomplete or unsupported maintenance output as an audit
   finding instead of normalizing it by hand.

Audit MUST NOT:

- pass `--write-state`, `--write`, `--write-cards` or equivalent mutation flags;
- write tracked repository files, maintenance baseline, board cards, delivery
  manifests, review verdicts or publish records;
- call external issue trackers, pull request APIs, comments or scheduler APIs.

## Triage Mode

Triage is bounded and preview-first.

1. Run or consume a schema-valid maintenance lifecycle report.
2. When annotations are supplied, validate them through:
   ```bash
   bin/changerail-maintenance triage --annotations <path> --json
   ```
3. Retain agent-authored annotations and preview outputs only under ignored
   `.runtime/changerail/maintenance/`.
4. Prepare or inspect card previews through:
   ```bash
   bin/changerail-maintenance cards --json
   ```
5. If and only if the operator explicitly supplies `--write-cards`, delegate to:
   ```bash
   bin/changerail-maintenance cards --write --json
   ```

`--write-cards` may create or update tracked board cards through the
deterministic card bridge, but it does not authorize commit, push, publish,
baseline writes, state writes or fixing source files. Any tracked board card
created from triage must proceed through the normal ChangeRail delivery,
independent review and publish gates.

## Safety Stops

Stop and report clearly when:

- the requested mode is not `audit` or `triage`;
- the requested work is a fix, delivery, publish, commit, push, external-system
  write or scheduler mutation;
- supplied reports or annotations are not schema-valid;
- triage cannot retain output under ignored `.runtime/changerail/maintenance/`;
- tracked card writes are requested without explicit `--write-cards`;
- maintenance output contains unsafe paths, secret-like values or
  machine-specific state that cannot be safely summarized;
- the user asks to pause, stop, review or change direction.

## Output

When done, summarize:

- mode and input source;
- deterministic commands run and observed outcomes;
- report, annotation or preview runtime paths;
- open findings or invalid-input findings;
- whether tracked files changed;
- exact next command for any follow-up, usually a normal board-card delivery
  command rather than a maintain fix.
