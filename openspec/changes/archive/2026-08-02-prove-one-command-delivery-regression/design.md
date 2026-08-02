## Context

`scripts/smoke-delivery-runner.py` already owns the local fake launcher, fake
Git, temporary repository and queue fixtures for the non-interactive runner.
Focused smokes currently prove command construction, preflight classification,
resume checks, terminal outcome parsing, fallback review evidence, metrics
inputs and queue behavior. The missing guard is an end-to-end regression fixture
that starts from a `deliver-ready` card and proves the observable state after
the runner-supervised `$changerail-deliver` path.

The fixture must remain generic ChangeRail core. It cannot use live network,
Codex credentials, private consumer repositories, raw logs in tracked files or
machine-specific paths.

## Goals / Non-Goals

**Goals:**

- Add a bounded temporary-repository smoke that uses a local bare remote and one
  runner entrypoint.
- Prove the success path leaves final card, Git history, manifest, verdict,
  evidence and runner status mutually consistent.
- Prove a transient remote preflight failure can stop, then resume after a fresh
  successful preflight.
- Prove stale verdict and exhausted review-budget paths fail closed without
  publishing.
- Wire the new smoke into the release baseline inventory.

**Non-Goals:**

- Do not run real Codex, consume network tokens or depend on an external remote.
- Do not replace focused runner, manifest, verdict or evidence smokes.
- Do not add new public runtime schemas unless the fixture exposes a schema gap.
- Do not model native Windows path behavior in this Linux-local fixture.

## Decisions

1. Reuse `scripts/smoke-delivery-runner.py` as the source of truth for runner
   integration coverage.

   The existing smoke already creates disposable repositories, fake launchers
   and runner status assertions. Extending it keeps release inventory simple and
   avoids another long-running test command in the baseline.

2. Implement a test-only fake one-command delivery child.

   In a new fake mode the launcher will read the supplied card path and mutate a
   temporary generic workspace as a successful delivery would: create or archive
   the planned change, sync a small spec/doc payload, write ignored manifest,
   evidence and review verdict files, move the card to `4.done`, commit the
   scoped payload and push to the local bare remote. The runner still invokes one
   child command; the fixture asserts observable repository state rather than
   transcript wording.

   Alternative considered: spawn real `$changerail-deliver` in the fixture.
   That would require real agent credentials and external review authority, so
   it is not acceptable for release baseline.

3. Keep failure paths deterministic through fake Git and fake child modes.

   The transient preflight scenario uses the existing fake Git reachability
   wrapper to produce a blocked remote preflight status, then reruns `resume`
   with a successful publish target and proves the resumed run publishes the
   same card. The fail-closed scenarios use fake child outputs and runtime
   evidence for stale verdict and exhausted review-budget `NO-GO`, then assert
   the card remains unpublished and no payload commit reaches the remote.

4. Validate scope through observable files and status schemas.

   The success fixture will inspect `status.json`, the final card, local/remote
   Git history, manifest committable paths, ignored evidence/verdict paths and
   `git status --short`. It will also assert that tracked card text does not
   contain mutable commit or push metadata and that manifest scope excludes
   runtime paths.

## Risks / Trade-offs

- [Risk] A fake child can drift from real skill behavior. -> Mitigation: assert
  stable contracts at file/status/schema boundaries and retain focused smokes
  for helper-specific behavior.
- [Risk] The fixture can become too slow for the release baseline. -> Mitigation:
  keep the repository minimal, avoid network, reuse local bare remotes and avoid
  subprocess sleeps outside existing bounded retry behavior.
- [Risk] Git history assertions can become brittle. -> Mitigation: check commit
  count, messages and path scope rather than exact hashes in tracked text.
- [Risk] Runtime evidence can leak into tracked payload. -> Mitigation: assert
  ignored runtime paths are not staged/committed and run public-surface scans in
  the normal release baseline.

## Migration Plan

1. Add delivery-runner and release-discipline delta requirements.
2. Extend `scripts/smoke-delivery-runner.py` with the one-command success,
   preflight resume and fail-closed fixtures.
3. Add a dedicated step to `scripts/run-release-baseline.py` if the new fixture
   is separated from the existing delivery runner smoke; otherwise update docs
   to state that `scripts/smoke-delivery-runner.py` includes this coverage.
4. Update release documentation/inventory.
5. Run focused smoke, OpenSpec validation, release baseline and public-surface
   scans.

## Open Questions

- none
