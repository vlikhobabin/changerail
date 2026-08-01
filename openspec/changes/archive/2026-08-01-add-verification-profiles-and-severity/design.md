## Context

`bin/verify-project` currently has two result channels:

- structural `Check` entries with boolean `ok`, where any failed check makes
  the run fail;
- `Advisory` entries such as delivery runner auth readiness, which are printed
  separately and do not affect the summary status.

That model is too coarse for consumers that intentionally use only part of the
ChangeRail surface or carry explicit project-wide baseline OpenSpec debt. The
new contract needs a stable profile/severity model while preserving the
fail-closed default for existing generated consumers and release verification.

Affected surfaces:

- `bin/verify-project`;
- `scripts/smoke-verify-project.py` and generated smoke fixtures;
- `templates/project/openspec/config.yaml.tpl` and generated guidance;
- `openspec/specs/changerail-project-verification/spec.md`,
  `openspec/specs/changerail-project-bootstrap/spec.md` and
  `openspec/specs/changerail-project-templates/spec.md`.

## Goals / Non-Goals

**Goals:**

- Make the verifier profile-aware for Codex, Claude and legacy MCP surfaces.
- Emit a stable JSON contract with separate `status` and `severity`.
- Allow `pass-with-diagnostics` only when all blocking checks pass.
- Keep targeted card-owned OpenSpec validation mandatory.
- Cover positive and negative behavior with deterministic smoke fixtures.

**Non-Goals:**

- Fixing existing project-wide OpenSpec debt automatically.
- Migrating real consumer repositories.
- Adding native Windows path/link semantics.
- Changing review/publish fail-closed gates.

## Decisions

1. **Use tracked OpenSpec config as the profile source.**
   `verify-project` will read an optional verification policy from
   `openspec/config.yaml`. Generated templates will include an explicit strict
   default. This keeps policy with project-owned rules and avoids ignored local
   state.

   Alternative considered: command-line flags. Flags are useful for diagnostics
   but not durable enough for reviewer or release evidence because they are easy
   to omit.

2. **Normalize checks to a single result type.**
   Replace boolean-only `Check` and separate `Advisory` handling with a unified
   result shape:

   ```text
   name, status, severity, message
   ```

   `status` describes what happened (`pass`, `fail`, `skip`). `severity`
   describes publish/verification impact (`blocking`, `non-blocking`, `info`).
   Summary status is derived only from normalized results.

   Alternative considered: keep advisories separate. That would preserve
   current output but leave `pass-with-diagnostics` and profile optionality
   without one machine-readable contract.

3. **Fail closed on invalid policy.**
   Unknown surface names, unknown states, attempts to weaken mandatory targeted
   validation and malformed baseline debt entries become blocking policy errors.
   A permissive parser would make typos look like accepted exemptions.

4. **Keep the default strict all-surfaces behavior.**
   Missing profile data or generated default config treats canonical Codex,
   Claude and helper surfaces as required and stale legacy artifacts as
   forbidden. Existing consumers and release checks should remain red/green
   unless they explicitly opt into diagnostics.

5. **Model project-wide baseline debt as explicit residual risk.**
   A baseline debt exemption must name the command, residual risk and why it is
   not card-owned. It can downgrade only project-wide baseline validation, not a
   targeted card-owned OpenSpec validation target.

## Risks / Trade-offs

- Invalid tracked policy could block a consumer that was previously green ->
  mitigation: generated templates use a minimal strict policy and smoke tests
  cover malformed/weakening fixtures.
- Text output changes could surprise scripts that parse free-form lines ->
  mitigation: keep `PASS`/`FAIL` prefixes for blocking checks where practical
  and document JSON as the stable contract.
- Baseline debt matching could accidentally mask fresh failures -> mitigation:
  require explicit command/risk/rationale and keep targeted validation
  mandatory.
- Optional surfaces could hide broken wiring in default consumers -> mitigation:
  missing policy preserves current strict all-surfaces behavior.

## Migration Plan

1. Add OpenSpec artifacts and validate the change.
2. Implement normalized result objects and summary derivation in
   `bin/verify-project`.
3. Parse `openspec/config.yaml` verification policy with fail-closed errors.
4. Update generated project config/guidance.
5. Extend smoke fixtures for Codex-only, default all-surfaces, forbidden
   artifact and mandatory-check weakening.
6. Run focused smokes, generated bootstrap/verify smoke, release baseline and
   public-surface scans.

Rollback is straightforward: remove the profile policy and normalized result
handling before archive. No external dependency or data migration is introduced.

## Open Questions

- none
