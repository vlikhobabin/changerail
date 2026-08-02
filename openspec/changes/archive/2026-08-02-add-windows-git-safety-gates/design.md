## Context

`030-03` made Git safety mandatory for generated, symlink and junction paths:
Windows verification must inspect porcelain status, dry-run staging and index
evidence before recommending stageable paths. `040-02` added fallback proof
fields and currently accepts retained Git evidence in fixture form, but the
project still lacks a reusable local Git safety helper and smoke fixtures that
prove safe and unsafe staging behavior across generated and link-like wiring.

## Goals / Non-Goals

**Goals:**
- Add deterministic Git safety checks that run `git status --porcelain`,
  `git add --dry-run` and index inspection for wiring paths.
- Cover generated, symlink and junction-style fixtures without requiring native
  Windows privileges on Linux release baseline.
- Fail closed when dry-run or index evidence would stage ChangeRail source,
  ignored runtime state, credentials or out-of-scope files.
- Cover rename/update/uninstall and partial cleanup scenarios.
- Keep `.gitignore` minimal and diagnostics sanitized.

**Non-Goals:**
- Не создавать реальные Windows junctions on Linux.
- Не claim two-host native Windows support; live host smoke belongs to later
  cards.
- Не stage or commit fixture repositories from smoke.

## Decisions

1. Add a local Git safety evaluator for fixtures.

   A focused helper inside smoke/test code can create temporary Git repositories,
   run the required Git commands and classify observed paths. Production
   fallback proof validation continues to require concrete evidence fields; the
   smoke proves those fields come from the expected command classes.

2. Model junction behavior with retained proof plus directory fixtures.

   Linux cannot create Windows junctions, so deterministic smoke should keep
   the proof contract as retained evidence and separately validate path
   classification, dry-run output and index behavior against fixture
   directories. Live junction creation remains a Windows lab concern.

3. Treat ignore expansion as a regression.

   The fixture should include project-owned source files near generated wiring
   and verify they remain visible to Git, while runtime/auth paths remain
   ignored or forbidden. This protects against solving safety by hiding too much
   in `.gitignore`.

4. Keep unsafe path diagnostics generic.

   Git safety output should name repository-relative paths and classes such as
   `runtime`, `credential` or `out-of-scope`; it must not print raw credential
   contents, private hostnames or private Windows absolute paths.

## Risks / Trade-offs

- [Risk] Local fixtures cannot prove native junction semantics.
  Mitigation: keep native junction support gated by proof files and mark live
  host smoke as downstream evidence.
- [Risk] `git add --dry-run` output can vary by Git version.
  Mitigation: parse path classes conservatively and assert command execution
  plus known fixture paths rather than brittle full output.
- [Risk] Safety checks may become too broad and hide project source.
  Mitigation: add a negative fixture that fails if minimal project-owned source
  is ignored or absent from status/dry-run evidence.
