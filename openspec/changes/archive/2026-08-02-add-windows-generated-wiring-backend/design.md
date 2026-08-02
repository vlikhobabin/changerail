## Context

`030-03` выбрал generated project-local wiring как native Windows default, а
`040-01` уже добавил `.cmd` entrypoints for supported helper commands. Текущий
`bin/bootstrap-project` создает templates и затем всегда создает symlink wiring
через `symlink_plan()`. `bin/verify-project` в свою очередь проверяет expected
surfaces как symlink-и. Это сохраняет POSIX behavior, но native Windows default
остается зависимым от privileges, которые architecture decision явно исключила.

Этот change вводит generated-copy backend только для bootstrap/adoption wiring.
Refresh, rollback and explicit symlink/junction fallbacks остаются во втором
change этой карточки.

## Goals / Non-Goals

**Goals:**
- Select generated-copy wiring by default on native Windows while keeping POSIX
  symlink wiring unchanged.
- Copy command, skill and helper wiring into the consumer project with
  generated ownership metadata.
- Record source identity, digest and refresh intent in a verifier-readable
  manifest or tracked project policy.
- Keep file wiring and directory wiring classified separately.
- Make dry-run report the selected backend, ownership plan and fallback reasons.

**Non-Goals:**
- Implement generated refresh or upgrade.
- Implement symlink/junction fallback modes.
- Claim live Windows host support without the later smoke/proof cards.
- Change Codex auth symlink behavior; auth remains explicit local opt-in.

## Decisions

1. Add a wiring backend abstraction around the existing symlink plan.

   Rationale: the current plan already lists the project surfaces that bootstrap
   must create. Reusing it avoids a second source of truth for commands, skills
   and helper wrappers. The backend chooses how each planned artifact is
   materialized: POSIX keeps relative symlink-и, native Windows uses generated
   copies.

2. Store generated ownership as project-tracked policy metadata.

   Rationale: `verify-project` needs to audit generated copies in a clean clone
   without ignored runtime state. A tracked manifest under project policy can
   record artifact relative path, kind (`file` or `directory`), source relative
   identity under ChangeRail, digest and owner state (`generated`). The manifest
   must avoid private local paths in portable mode.

3. Copy directory surfaces as generated directory trees and helper wrappers as
   generated files.

   Rationale: Codex and Claude skills/commands are directory surfaces, while
   helper wrappers are file surfaces. Treating them separately lets verification
   report precise drift and prevents future cleanup from recursing through a
   link target.

4. Prefer platform default with tracked policy override.

   Rationale: native Windows needs a deterministic default, but consumer
   projects may need to preserve POSIX symlink wiring or explicitly opt into a
   fallback later. The first change reads platform and project policy only for
   generated default selection; the second change adds explicit fallback gates.

## Risks / Trade-offs

- [Risk] Generated copies can drift from ChangeRail source. Mitigation: record
  source identity and digest now; implement blocking stale-copy verification and
  refresh in the dependent change.
- [Risk] Copying complete skill directories increases tracked file count in
  Windows consumers. Mitigation: generated ownership metadata makes those files
  recognizable and refreshable, and POSIX consumers keep symlink wiring.
- [Risk] Portable manifests might leak local source paths. Mitigation: store
  source paths relative to ChangeRail root and keep absolute labels only in
  explicit local config mode.
- [Risk] Generated copies may accidentally overwrite project-owned files.
  Mitigation: this change creates generated files only for fresh bootstrap or
  replacement of generated-owned surfaces; project-owned divergence handling is
  completed by the second change.

## Open Questions

- The exact tracked manifest filename should align with existing generated
  project policy files during implementation.
- Whether adoption of an existing project needs a separate command surface can
  remain out of scope if bootstrap owns all current generated consumer creation.
