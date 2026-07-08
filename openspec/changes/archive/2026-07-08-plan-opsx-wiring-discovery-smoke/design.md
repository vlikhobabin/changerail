## Context

The architecture defines consumer wiring through symlinks to `/opt/opsx`, while
the minimal skill surface now provides source files for `opsx-explore` and
`opsx-ff`. A previous review found that command wrappers can accidentally assume
a root `skills/` path that does not exist in consumer repositories. This
delivery pass makes discovery assumptions executable and testable.

## Goals / Non-Goals

**Goals:**
- Specify consumer wiring that matches the architecture.
- Specify repo-local dogfooding wiring for `/opt/opsx`.
- Require smoke evidence that agents can discover `opsx-explore` and
  `opsx-ff`.
- Keep all examples public-safe and generic.

**Non-Goals:**
- Do not add `opsx-do`, `opsx-review`, `opsx-pub` or `opsx-deliver`.
- Do not commit local `.claude/settings.local.json`, runtime state or machine
  inventory.
- Do not create machine-local absolute symlink-и or tracked runtime reports.

## Decisions

- Consumer Claude wiring follows the architecture: `.claude/skills` resolves to
  OPSX `skills/`, and `.claude/commands/opsx` resolves to OPSX
  `claude/commands/opsx`.
- Consumer Codex wiring uses per-skill links or generated copies under
  `.codex/skills/opsx-*`, not Codex runtime state.
- Repo-local dogfooding for `/opt/opsx` uses relative symlinks as the first
  smoke target:
  - `.claude/skills -> ../skills`
  - `.claude/commands/opsx -> ../../claude/commands/opsx`
  - `.codex/skills/opsx-explore -> ../../skills/opsx-explore`
  - `.codex/skills/opsx-ff -> ../../skills/opsx-ff`
  These links stay inside the repository and do not point to another workspace.
- Smoke checks should verify discovery, not implementation behavior: the smoke
  should prove that the command/skill is visible and loads the expected
  contract.
- Consumer smoke uses a temporary example project under ignored
  `.runtime/opsx/wiring-smoke/<run-id>/example-project`. The smoke creates the
  documented links there, checks their resolved targets and records evidence
  without committing runtime output.
- Committable evidence for smoke support is limited to docs/scripts and sample
  schemas. Runtime evidence is ignored and referenced only from summaries.
- The delivery pass adds:
  - `docs/wiring-discovery.md` describing consumer and repo-local wiring.
  - `scripts/smoke-wiring-discovery.py` for deterministic filesystem/discovery
    checks.
  - repo-local relative symlink-и for `.claude/skills`,
    `.claude/commands/opsx`, `.codex/skills/opsx-explore` and
    `.codex/skills/opsx-ff`.

## Evidence Contract

The implementation smoke MUST produce a JSON report in ignored runtime space:

```text
.runtime/opsx/wiring-smoke/<run-id>/report.json
```

The report is aggregate because a normal smoke run covers both modes and both
surfaces. Minimum top-level report fields:

- `schema`: `opsx.wiring-discovery-smoke.v1`
- `run_id`
- `opsx_root`
- `report_kind`: `aggregate`
- `modes[]`: includes `repo-local` and `consumer-example` for a full run
- `surfaces[]`: includes `claude` and `codex` for a full run
- `summary`
- `runs[]`
- `checks[]`

Each `runs[]` entry MUST include:

- `mode`: `repo-local` or `consumer-example`
- `surface`: `claude` or `codex`
- `summary`
- `checks[]`

Each `checks[]` entry, whether top-level aggregate or per-run, MUST include:

- `name`
- `path`
- `expected_target`
- `resolved_target`
- `status`: `pass` or `fail`
- `message`
- `mode`
- `surface`

Minimum pass criteria:

- Claude repo-local check proves `.claude/skills` and
  `.claude/commands/opsx` resolve inside `/opt/opsx`.
- Claude consumer check proves `.claude/skills` and
  `.claude/commands/opsx` resolve to OPSX source paths from the example project.
- Codex repo-local check proves `.codex/skills/opsx-explore` and
  `.codex/skills/opsx-ff` resolve inside `/opt/opsx`.
- Codex consumer check proves `.codex/skills/opsx-explore` and
  `.codex/skills/opsx-ff` resolve to OPSX source paths from the example project.
- Skill contract check proves both `SKILL.md` files have matching frontmatter
  `name` values.
- Command wrapper check proves `/opsx:explore` and `/opsx:ff` wrappers do not
  reference a consumer-root `skills/` path.

The verification summary must cite the command that generated the report and
the report path. The report itself remains ignored runtime state.

## Risks / Trade-offs

- Symlink discovery can differ between agent runtimes -> smoke must cover both
  Claude and Codex surfaces before declaring wiring stable.
- Absolute symlinks to private workspaces leak local paths -> only documented
  generic `/opt/opsx` examples are allowed in public files.
- Wiring the current repo too early could mask consumer failures -> include both
  repo-local and example consumer checks.

## Migration Plan

1. Implement `docs/wiring-discovery.md`.
2. Implement `scripts/smoke-wiring-discovery.py`.
3. Run repo-local smoke against `/opt/opsx`.
4. Run consumer-example smoke under `.runtime/opsx/wiring-smoke/<run-id>/`.
5. Record the ignored report path in verification summaries.
6. Run public-surface scans to confirm no local/private paths are committed.

## Open Questions

- Whether consumer bootstrap should default to symlinks or generated copies for
  Claude skills if future CLI behavior changes.
