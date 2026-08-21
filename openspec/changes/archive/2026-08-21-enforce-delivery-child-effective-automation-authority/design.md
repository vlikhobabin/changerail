## Context

Single-card runner проверяет effective config до запуска child и затем строит
команду `<launcher> exec --json ...`. Для default tracked launcher это означает
запуск Codex только с config-layer `never`/`danger-full-access`. В обычном
процессе этого достаточно, но outer/nested execution boundary может наложить
отдельный sandbox на model-generated commands. Supervisor-side Git proof тогда
не эквивалентен реальному child.

User-controlled separate runner `CODEX_HOME` уже является явным выбором
operator-owned unattended authority. Фикс должен сделать именно эту
существующую authority effective, не превращая dangerous bypass в generic
default.

## Goals / Non-Goals

**Goals:**

- Make trusted automation authority effective at the real tracked Codex child.
- Fail before launch if the installed Codex CLI cannot support the required
  invocation mode.
- Preserve all existing config, auth, cleanliness, upstream and publish-target
  gates.
- Preserve custom launcher and generated-home behavior.

**Non-Goals:**

- No new mutation authority, status schema fields or protocol version.
- No automatic bypass for project-generated runtime homes.
- No Codex-specific flags for custom launchers.
- No SSH config rewrite, credential access or remote-specific workaround.

## Decisions

1. **Use explicit operator-owned `CODEX_HOME` as the opt-in boundary.**
   The bypass is selected only when `CODEX_HOME` was explicitly present in the
   runner environment, the configured launcher resolves to tracked
   `/opt/changerail/bin/codex`, and the existing authority check has accepted
   exact `never`/`danger-full-access`. Generated default homes remain config-
   driven and unchanged.

2. **Propagate authority at Codex invocation level.**
   The runner places `--dangerously-bypass-approvals-and-sandbox` before
   `exec`. This is the Codex CLI surface that prevents an outer command sandbox
   from silently narrowing already-approved unattended authority. The command
   remains visible in existing `command.argv`; no wire field is added.

3. **Probe CLI capability during preflight.**
   For the exact explicit-home/tracked-launcher route, preflight runs the
   installed `codex exec --help` and requires the bypass option to be
   advertised. Missing binary, timeout, execution error or missing option is a
   blocking `Codex effective automation authority` check. No child is launched
   on failure.

4. **Keep custom launchers untouched.**
   A custom launcher may wrap a different supported execution surface. The
   runner neither injects a Codex-specific flag nor claims to validate that
   launcher's internal authority propagation. Existing custom-launcher checks
   and behavior remain unchanged.

5. **Test through the real tracked wrapper without a real model.**
   A fake `codex` binary is placed first on a temporary `PATH`. The test invokes
   the actual tracked `bin/codex`, observes both the runner status argv and the
   binary-received argv, and proves the bypass precedes `exec`. A second case
   proves unsupported CLI capability blocks before the delivery invocation.

## Risks / Trade-offs

- [Risk] The Codex bypass removes child-side confirmation and sandboxing.
  Mitigation: it is available only after explicit operator-home selection and
  the existing exact trusted automation policy gate; the card is reviewed as
  critical/xhigh.
- [Risk] Codex CLI option drift could break automation.
  Mitigation: capability preflight fails before mutation instead of discovering
  drift inside delivery.
- [Risk] Generated-home users can still encounter a nested sandbox mismatch.
  Mitigation: the dangerous route is not silently broadened; operators who need
  effective unattended authority must select an explicit isolated home.

## Migration Plan

1. Add focused RED coverage for missing invocation-level propagation.
2. Add the capability check and command construction change.
3. Update docs/spec and run focused plus full release verification.
4. Consumers that require nested unattended delivery update their ChangeRail
   lock and invoke the runner with their existing explicit isolated
   `CODEX_HOME`.

Rollback is a scoped revert before consumer lock updates. No wire or data
migration is required.

## Open Questions

- none
