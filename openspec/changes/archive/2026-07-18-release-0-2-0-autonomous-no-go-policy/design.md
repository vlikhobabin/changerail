## Context

ChangeRail already has release discipline docs, a root `VERSION`, root
`CHANGELOG.md`, compatibility notes and migration guide. `0.1.0` is the current
public baseline. Since then, `Unreleased` accumulated rename, runner, metrics,
schema, release gate and public-safety changes. The active
`add-autonomous-no-go-rescue-policy` change adds one more public workflow
contract change and is the trigger to publish a pre-stable minor release.

Repository guidance keeps release tags and packaged distribution metadata as
planned public surface after the first stable release decision. Therefore this
change prepares a reviewed release payload but does not create a git tag.

## Goals / Non-Goals

**Goals:**
- Bump root version to `0.2.0`.
- Move accumulated `Unreleased` changelog entries into a dated `0.2.0` section.
- Add explicit `0.1.0 -> 0.2.0` migration notes.
- Document the autonomous `NO-GO` policy migration for symlink-based consumers
  and local-copy consumers.
- Keep examples generic and public-safe.

**Non-Goals:**
- Do not create a git tag or GitHub release in this card.
- Do not alter executable MCP pins, OpenSpec pin, schemas or helper behavior.
- Do not archive the autonomous policy change; that remains a separate
  lifecycle step.

## Decisions

1. **Treat `0.2.0` as a pre-stable minor release.**
   The new policy changes agent behavior and public skill contract, so it is
   not a patch release. Pre-`1.0.0` minor releases can carry workflow contract
   changes when changelog and migration guide are explicit.

2. **Promote all current `Unreleased` entries.**
   The release should publish the full accumulated public surface since
   `0.1.0`, not only the newest policy line. This gives consumers one coherent
   target version.

3. **Migration is verification plus session refresh for symlink consumers.**
   Projects that use ChangeRail symlinks pick up updated skills from the source
   checkout. They still need `/opt/changerail/bin/verify-project` and active
   Claude/Codex session restart so loaded skill text is refreshed.

4. **Local-copy consumers need explicit file refresh.**
   If a project copied lifecycle skills or docs instead of symlinking
   `/opt/changerail`, migration notes must tell it to refresh `changerail-deliver`
   and related instructions manually.

## Risks / Trade-offs

- [Risk] Calling this a release without a tag can confuse external consumers.
  → Mitigation: docs state this is a reviewed pre-stable release payload; tags
  remain planned until stable release policy enables them.
- [Risk] Existing autonomous sessions keep old skill text in memory.
  → Mitigation: migration notes require stopping/restarting active sessions.
- [Risk] Consumers miss the behavior change because no file rewiring is needed.
  → Mitigation: mark the workflow contract change as `BREAKING:` in changelog
  and migration notes.
