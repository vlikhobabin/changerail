# Исследовать и закрыть installed-origin boundary affected profile v7

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 18S

## Source
- Latest safe published affected v6 authorization, exact tip
  `042868b2278c2505353de516b87f94f9463be908`.
- Published admission/bounds rescue, integration decision, semantic scheduler
  v1 and affected v5/v6 authorizations.
- Unpublished `implement-bounded-affected-release-profile-v6` ended after its
  sole repair in terminal review-cycle-2 `NO-GO`; its payload and runtime state
  are forensic-only and cannot satisfy future delivery gates.

## Summary
Опубликовать docs-only investigation/design boundary для clean affected v7:
installed distribution origins допускаются только из exact `purelib`/`platlib`
effective-interpreter paths, а connected production-default proof обязан
отклонять `stdlib`, `scripts`, `data`, `include` и любой иной `sysconfig` root.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Lineage escalation: terminal v6 exhausted its same-card repair on the same
  installed-origin blocker class, so further implementation requires this
  separate docs-only investigation/design boundary.
- Independent review: one fresh `gpt-5.6-sol`/`high`
- Same-card repair budget limit/used/remaining: `1/0/1`, exhausted `false`

## Depends On
- `rescue-affected-release-profile-admission-bounds-boundary-v6`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`
- `authorize-bounded-affected-release-profile-v5`
- `authorize-bounded-affected-release-profile-v6`

## Blocks
- `authorize-bounded-affected-release-profile-v7`
- `implement-bounded-affected-release-profile-v7`
- `certify-accelerated-release-loop-v1`

## Authorization
- Future v7 implementation authorization:
  `{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-installed-origin-boundary-v7.md","investigation_id":"rescue-affected-release-profile-installed-origin-boundary-v7","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v7.md","successor_id":"implement-bounded-affected-release-profile-v7","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Decision публикуется docs-only от exact safe v6 authorization tip
  `042868b...`; remote rescue branch начинается ровно от этого SHA, а terminal
  v6 payload не читается, не копируется, не cherry-pick-ится и не принимается.
- Card переносит concise terminal chronology: cycle 1 `NO-GO` имел `7/12` и
  три blocker, единственная repair закрыла scheduler/authority и connected
  proof; cycle 2 `NO-GO` имел `11/12` и один installed-origin blocker.
- Единственный future order: эта investigation/design decision, docs-only
  `authorize-bounded-affected-release-profile-v7`, clean
  `implement-bounded-affected-release-profile-v7`, затем certification.
- Future authorization содержит ровно один exact six-field object выше,
  зависит ровно от этой decision, integration decision, scheduler v1 и v6
  authorization и блокирует только v7 implementation.
- Future implementation использует только
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v7.md","authorization_id":"authorize-bounded-affected-release-profile-v7"}`,
  зависит от пяти published predecessors выше плюс authorization v7, блокирует
  только certification, начинается от authorization-publishing HEAD и
  добавляет не более 499 production LOC.
- Effective Python identity и package roots вычисляются fail closed: allowed
  distribution origins — только resolved exact `sysconfig.get_paths()` values
  для keys `purelib` и `platlib`; missing, wrong-type, duplicate ambiguity,
  symlink/resolve error или любой другой key/root отклоняются до semantics.
- Каждая exact runtime/dev distribution обязана иметь exact pin и
  `locate_file("")` origin, равный одному из двух admitted package roots;
  `stdlib`, `platstdlib`, `scripts`, `data`, `include` и произвольный existing
  path не являются package origins.
- Ruff `0.6.9` обязан одновременно иметь exact framed version, installed
  distribution origin в admitted package roots и executable origin в exact
  selected interpreter `bin`; OpenSpec сохраняет exact offline `1.3.1`.
- Focused proof содержит production-default happy neighbor и connected
  counterexamples для каждого non-package `sysconfig` root, wrong package
  origin, wrong pin/version и effective Python/Ruff origin; explicit injected
  allowlist не может скрывать default-path over-admission.
- Future v7 сохраняет retained pre-production RED chronology и весь repaired
  v6 floor: exact 35→30 ownership, aggregate pre-mutation admission, strict
  four-stream bounds, connected resolved-base/runtime/count/order guards,
  exact typed scheduler `jobs 1|4`, full-only authority, four-step CI и
  protocol-artifact non-authority.
- Decision добавляет production/test/runtime LOC `0`, не создаёт v7 successors
  и не запускает history, real full/affected execution, benchmark, live matrix
  или certification checks.

## Change Set
- `rescue-affected-release-profile-installed-origin-boundary-v7`

## Verify
- GREEN retained: `safe-base-origin-rescue-v7-final` and
  `docs-final-green-origin-rescue-v7-final` prove exact safe-base/remote binding,
  terminal chronology, successor absence,
  six-field authorization, exact package-root decision, v6 preserved floor,
  strict OpenSpec, JSON/TOML, source classification, current-only public scan,
  whitespace, archive/main sync and manifest scope; ordinary/high preflight.
- RED: not applicable; this docs-only investigation/design adds no executable behavior.
- Prohibited: history, real full baseline, affected execution/benchmark, live
  matrix, successor creation/implementation and certification.

## Archive
- `openspec/changes/archive/2026-08-27-rescue-affected-release-profile-installed-origin-boundary-v7/`

## Related
- `openspec/changes/rescue-affected-release-profile-installed-origin-boundary-v7/`
- `openspec/board/4.done/authorize-bounded-affected-release-profile-v6.md`
- `openspec/board/4.done/rescue-affected-release-profile-admission-bounds-boundary-v6.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
DO complete: one docs-only investigation/design decision is synchronized and
archived. Exact v7 lineage, effective-interpreter package-root admission and
connected production-default proof are review-ready; successors and executable
payload remain absent.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `rescue-affected-release-profile-installed-origin-boundary-v7`

### Why
Affected v6 exhausted its sole repair because the default installed-origin
allowlist admitted non-package `sysconfig` roots; another same-card patch or
direct implementation successor would violate lifecycle policy.

### Goal
Publish one clean docs-only investigation/design decision that makes the v7
effective-interpreter package-root and connected default-path proof exact.

### Scope
- this card;
- same-slug OpenSpec artifacts;
- synchronized `changerail-release-ci` specification and archive metadata.

### Acceptance
- Exact lineage, terminal-attempt summary, package-root/origin decision,
  production-default counterexamples, preserved v6 floor, LOC, dormancy and
  prohibited-suite boundaries above are synchronized.

### Depends On
- `rescue-affected-release-profile-admission-bounds-boundary-v6`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`
- `authorize-bounded-affected-release-profile-v5`
- `authorize-bounded-affected-release-profile-v6`

### Related
- `openspec/changes/rescue-affected-release-profile-installed-origin-boundary-v7/`

## Log
- 2026-08-27 created in a clean worktree from exact safe v6 authorization tip;
  remote rescue branch was bound to that exact SHA and terminal v6 payload was
  not imported or executed.
- 2026-08-27 FF produced one apply-ready docs-only investigation/design change;
  v7 successors, executable LOC and prohibited evidence remain absent.
- 2026-08-27 DO synchronized four release-CI requirements, archived the
  same-slug change and preserved exact package-root/default-proof, clean v7
  lineage and repaired v6 floor with production/test/runtime LOC `0`.
- 2026-08-27T10:57:18Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
