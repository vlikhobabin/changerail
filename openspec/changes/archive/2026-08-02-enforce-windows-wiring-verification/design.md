## Context

`040-02` добавил generated-copy backend, tracked
`openspec/changerail-wiring.json`, refresh command и baseline fallback proof
validation. `bin/verify-project` уже умеет читать manifest и сравнивать source
identity/digest, а `scripts/smoke-verify-project.py` содержит первые fixtures
для stale и project-owned generated copies. Этот change превращает эти pieces
в явный verification/drift gate: generated Windows consumer должен pass только
когда manifest-owned artifacts действительно fresh, а stale/missing/diverged
state должен быть виден и для direct verify, и для workspace drift.

## Goals / Non-Goals

**Goals:**
- Сделать generated wiring checks observable через stable `verify-project`
  check names/messages и JSON summary.
- Покрыть valid, stale, missing, project-owned divergence и refresh smoke cases.
- Дать drift gate machine-readable class/message для stale generated wiring.
- Сохранить POSIX symlink verification без новых copy requirements.
- Не печатать credential contents, private hostnames или raw Windows paths.

**Non-Goals:**
- Не добавлять live two-host Windows smoke; это остается за downstream smoke
  cards.
- Не менять manifest schema beyond existing `changerail.generated-wiring.v1`,
  если для smoke хватает current fields.
- Не перезаписывать project-owned files silently during verification.

## Decisions

1. Treat `verify-project` as source of truth for freshness.

   Drift gate should keep invoking `bin/verify-project --json` and classify
   generated drift from verifier summary/check messages. This avoids a second
   digest implementation in `scripts/smoke-drift.py` and keeps remediation text
   consistent.

2. Keep generated checks path-scoped.

   Each manifest artifact should produce a check tied to its project-relative
   path. Missing metadata, missing destination, stale digest and project-owned
   divergence remain distinct messages so smoke and reviewer can see which
   acceptance criterion failed.

3. Add deterministic local fixtures instead of live Windows assumptions.

   Smoke creates generated projects under ignored `.runtime/`, mutates copies
   and manifest entries, then validates command outcome. This proves fail-closed
   behavior on Linux while leaving live host support to later evidence cards.

4. Use generic diagnostics.

   Messages may mention repository-relative paths and generic remediation such
   as `bin/bootstrap-project <project> --refresh-wiring`; they must not echo
   raw credential contents, private hostnames or private Windows absolute paths.

## Risks / Trade-offs

- [Risk] Drift gate may only see verifier text for exact failure subtype.
  Mitigation: assert stable summary/check fields in JSON smoke and keep
  free-text matching limited to remediation phrases.
- [Risk] Generated directory digest can be expensive for large skill trees.
  Mitigation: current wiring tree is small and digest is already used by
  bootstrap; no extra live scan is added outside verifier invocations.
- [Risk] Refresh smoke could accidentally overwrite a project-owned fixture.
  Mitigation: fixtures mutate generated-owned and project-owned states
  separately and assert project-owned divergence remains blocking.
