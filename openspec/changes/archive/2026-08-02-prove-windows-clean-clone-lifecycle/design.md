## Context

Серия `040-native-windows-implementation` уже добавила `.cmd` entrypoints,
generated-copy Windows wiring, verifier/drift/Git safety checks and aggregate
Windows smoke matrix. Финальная карточка должна связать эти части в один
end-to-end proof: на каждом Windows host начать с disposable clean clone,
создать generated-copy consumer project, проверить discovery/verification,
refresh/update и scoped no-push safety.

Текущий live matrix запускает readiness и runtime/wiring probes, но не клонирует
реальный ChangeRail checkout и не прогоняет consumer lifecycle against tracked
helpers. Также `bootstrap-project` пока не имеет `.cmd` wrapper, хотя именно он
создает consumer wiring.

## Goals / Non-Goals

**Goals:**
- Добавить native Windows `.cmd` wrapper для `bootstrap-project`.
- Добавить live proof harness, который использует ignored inventory,
  disposable host roots and sanitized reports.
- Встроить proof в `scripts/smoke-windows-matrix.py --live`.
- Проверить clean clone, `.cmd` entrypoints, generated-copy bootstrap,
  `verify-project`, discovery, refresh and explicit no-push staging fixture.

**Non-Goals:**
- Не запускать real Codex delivery на Windows hosts и не требовать Codex auth.
- Не переносить private SSH targets, usernames, disposable roots или raw host
  output в tracked files.
- Не менять Windows fallback defaults: symlink/junction остаются explicit
  fallback modes.

## Decisions

1. Proof harness as tracked Python helper.
   - Add `scripts/windows-clean-clone-lifecycle.py` with `dry-run` and `run`
     modes, following the existing Windows probe shape.
   - Rationale: public tracked code makes the support proof reproducible, while
     ignored inventory and runtime reports keep private host data out of Git.
   - Alternative: record manual notes only. Rejected because support claim must
     be repeatable and reviewable.

2. Clone public repository URL and verify exact ref.
   - The live harness accepts `--repo-url`, `--branch` and `--ref`; matrix passes
     the current workspace `HEAD`.
   - Rationale: clean-clone proof must run the reviewed source, not a manually
     edited copied tree.
   - Alternative: transfer local files over SSH. Rejected because it would not
     prove clean clone behavior.

3. Scoped no-push delivery smoke as Git safety fixture.
   - The harness creates a generated consumer, initializes Git, stages only an
     explicit tracked file set with `git add -- <paths>`, and proves ignored
     runtime files stay unstaged.
   - Rationale: the card acceptance is about scoped no-push staging safety; real
     Codex delivery would add external auth and model dependency unrelated to
     Windows runtime support.
   - Alternative: run `changerail-delivery-runner` live with Codex. Rejected for
     default proof because Windows lab inventory must not depend on agent auth.

4. Aggregate live matrix item.
   - `scripts/smoke-windows-matrix.py --live` runs the clean-clone lifecycle
     after existing live readiness/runtime checks.
   - Rationale: maintainers already have one Windows support smoke command, and
     the final support claim should cite one aggregate live matrix report plus
     the child lifecycle report.

## Risks / Trade-offs

- [Risk] Windows hosts cannot reach the public repository or npm/OpenSpec
  dependencies during live proof. -> Mitigation: record sanitized blocker and
  do not claim full support from that run.
- [Risk] Remote raw output contains private host paths. -> Mitigation: raw
  output stays under ignored `.runtime/changerail/`; tracked summaries use only
  generic host ids, outcome and relative ignored evidence paths.
- [Risk] The scoped delivery smoke is narrower than real delivery. ->
  Mitigation: call it an explicit staging/no-push safety fixture and keep real
  Codex delivery outside the Windows support proof.
