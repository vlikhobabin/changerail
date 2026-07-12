# Автоматизировать follow-up улучшения delivery pipeline

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Post-delivery retrospective for
  `openspec/board/4.done/harden-two-agent-workflow-contract.md`.

## Summary
Снизить долю ручной discipline в ChangeRail delivery pipeline: сделать archive
idempotent при уже синхронизированных specs, автоматизировать derivation
delivery manifest, стандартизировать fresh-review orchestration, добавить
единый public-surface scan helper, автоматизировать post-publish card
finalization и закрепить smoke coverage для workflow guidance в generated
consumer files.

## Acceptance
- `openspec archive` корректно обрабатывает already-synced requirements:
  либо idempotently skips duplicate main-spec requirements, либо явно и
  диагностично предлагает повторить команду с `--skip-specs`.
- Delivery manifest можно получить или обновить helper-ом из board card,
  archived changes и `git status`, а `staging-plan` остается reviewable и
  scoped к card-owned payload.
- `changerail-deliver` имеет стандартный fresh-review launch/resume protocol:
  готовый prompt/contract для reviewer-а, проверку
  `reviewer.independence`, `--check-fresh` validation и понятный safety stop,
  если fresh reviewer недоступен.
- `scripts/public-surface-scan.py` предоставляет единый allowlist для generic
  examples (`/opt/changerail`, `/opt/example-*`) и documented historical
  `opsx` references, а default public scan покрывает tracked OpenSpec
  artifacts including archived changes, чтобы обязательный public scan не
  зависел от ad hoc `rg` regex.
- `changerail-pub` или связанный helper автоматизирует deterministic
  finalization: move `3.inprogress -> 4.done`, update result/log/commit/push,
  amend card-only diff, update ignored delivery manifest and avoid substantive
  post-review edits.
- Bootstrap/render smoke проверяет, что generated `AGENTS.md` и
  `openspec/board/README.md` содержат актуальный workflow guidance:
  `explore -> ff -> do -> review -> pub`, role model, fresh review gate and
  board finalization boundary.
- Новые или измененные helpers имеют focused smoke/negative coverage; общий
  baseline `./bin/openspec validate --all --strict` и `git diff --check`
  проходит.

## Change Set
- `make-archive-sync-idempotent`
- `derive-delivery-manifest`
- `automate-review-and-publish-finalization`
- `add-public-surface-scan-helper`
- `add-bootstrap-workflow-guidance-smoke`

## Verify
- passed: `bash -n bin/openspec`
- passed: `python3 -m py_compile bin/bootstrap-project bin/verify-project scripts/changerail_review_verdict.py scripts/changerail_delivery_manifest.py scripts/public-surface-scan.py scripts/smoke-bootstrap-project.py scripts/smoke-delivery-manifest.py scripts/smoke-delivery-manifest-derive.py scripts/smoke-openspec-archive-diagnostics.py scripts/smoke-release-ci.py scripts/smoke-verify-project.py scripts/smoke-wiring-discovery.py`
- passed: `python3 scripts/smoke-openspec-archive-diagnostics.py`
- passed: `python3 scripts/smoke-delivery-manifest.py`
- passed: `python3 scripts/smoke-delivery-manifest-derive.py`
- passed: `python3 scripts/public-surface-scan.py --self-test`
- passed: `python3 scripts/public-surface-scan.py`
- passed: `python3 scripts/public-surface-scan.py openspec/changes/archive`
- passed: `python3 scripts/smoke-bootstrap-project.py`
- passed: `python3 scripts/smoke-release-ci.py`
- passed: `python3 scripts/smoke-review-verdict-validation.py`
- passed: `python3 -m json.tool .mcp.json`
- passed: TOML parse for `.codex/config.toml`
- passed: `./bin/openspec validate make-archive-sync-idempotent --strict`
- passed: `./bin/openspec validate derive-delivery-manifest --strict`
- passed: `./bin/openspec validate automate-review-and-publish-finalization --strict`
- passed: `./bin/openspec validate add-public-surface-scan-helper --strict`
- passed: `./bin/openspec validate add-bootstrap-workflow-guidance-smoke --strict`
- passed: `./bin/openspec validate --all --strict` before archive (18/18)
- passed: `./bin/openspec validate --all --strict` after archive (13/13)
- passed: `git diff --check`

## Archive
- `openspec/changes/archive/2026-07-12-make-archive-sync-idempotent/`
- `openspec/changes/archive/2026-07-12-derive-delivery-manifest/`
- `openspec/changes/archive/2026-07-12-automate-review-and-publish-finalization/`
- `openspec/changes/archive/2026-07-12-add-public-surface-scan-helper/`
- `openspec/changes/archive/2026-07-12-add-bootstrap-workflow-guidance-smoke/`

## Related
- `openspec/board/4.done/harden-two-agent-workflow-contract.md`
- `bin/openspec`
- `scripts/changerail_delivery_manifest.py`
- `skills/changerail-deliver/SKILL.md`
- `skills/changerail-pub/SKILL.md`
- `scripts/`
- `bin/bootstrap-project`
- `templates/project/AGENTS.md.tpl`
- `templates/project/openspec/board/README.md.tpl`
- `openspec/changes/archive/2026-07-12-make-archive-sync-idempotent/`
- `openspec/changes/archive/2026-07-12-derive-delivery-manifest/`
- `openspec/changes/archive/2026-07-12-automate-review-and-publish-finalization/`
- `openspec/changes/archive/2026-07-12-add-public-surface-scan-helper/`
- `openspec/changes/archive/2026-07-12-add-bootstrap-workflow-guidance-smoke/`

## Result
Implemented and archived. The pipeline now has diagnostic handling for
already-synced archive conflicts, derived delivery manifests with publish/card
finalization helper commands, a standard fresh-review prompt in
`changerail-deliver`, deterministic finalization guidance in `changerail-pub`,
a reusable public-surface scanner whose default roots include archived OpenSpec
artifacts, and bootstrap smoke coverage for generated workflow guidance.

Published reviewed payload as `82e6b3e4c70e0a33db55be284458642f05496d76`; push status `pending` on `main`/`origin`.

## Next
- done

## Change 1: `make-archive-sync-idempotent`

### Why
Archive currently aborts when delta `ADDED Requirements` were already synced
manually into main specs, forcing the operator to know about `--skip-specs`.

### Goal
Make archive behavior deterministic and self-explanatory for already-synced
requirements.

### Acceptance
- Duplicate already-synced requirements do not produce confusing archive
  failure.
- If automatic skip is unsafe, the diagnostic explicitly recommends
  `--skip-specs` and explains why.
- Smoke coverage exercises duplicate requirement handling.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-12-make-archive-sync-idempotent/`

## Change 2: `derive-delivery-manifest`

### Why
Manual delivery manifests are easy to make incomplete on broad cards.

### Goal
Add or extend `scripts/changerail_delivery_manifest.py` so it can derive/update
a manifest from a board card, archived changes and current git status.

### Acceptance
- Helper can create/update `.runtime/changerail/delivery-manifests/<card-id>.json`.
- Generated `committable_paths` cover card, archives, synced specs and changed
  payload files without including ignored runtime state.
- Existing `validate` and `staging-plan` remain compatible.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-12-derive-delivery-manifest/`

## Change 3: `automate-review-and-publish-finalization`

### Why
Fresh reviewer launch and post-publish card finalization worked, but required
manual orchestration and card-only amend steps.

### Goal
Strengthen `changerail-deliver` and `changerail-pub` contracts/helpers so
review launch/resume and deterministic card finalization are standard pipeline
behavior.

### Acceptance
- `changerail-deliver` documents a ready-to-run fresh reviewer prompt or helper
  invocation and validates `reviewer.independence` plus freshness before
  continuing.
- `changerail-pub` documents or uses helper behavior for final card move,
  result/log/commit/push metadata, card-only amend and manifest publish update.
- Safety stops are explicit when fresh reviewer launch, finalization or amend
  cannot be completed without substantive post-review edits.

### Depends On
- `derive-delivery-manifest`

### Related
- `openspec/changes/archive/2026-07-12-automate-review-and-publish-finalization/`

## Change 4: `add-public-surface-scan-helper`

### Why
Public-surface scans are currently hand-written shell/regex commands and can
fail due to tool-specific regex behavior.

### Goal
Add a stable scanner with project-owned allowlists and clear pass/fail output.

### Acceptance
- `scripts/public-surface-scan.py` scans explicit paths or default public
  surfaces.
- Allowed examples include `/opt/changerail`, `/opt/example-project`,
  `/opt/example-a`, `/opt/example-b` and documented historical `opsx`
  references.
- Negative smoke fixture fails on a non-allowed `/opt/<private>` path.
- Default scan covers tracked OpenSpec archive artifacts and fails on disallowed
  private `/opt/*` paths there.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-12-add-public-surface-scan-helper/`

## Change 5: `add-bootstrap-workflow-guidance-smoke`

### Why
Reviewer had to manually render a temporary bootstrap project to confirm that
consumer templates propagate workflow guidance.

### Goal
Add stable smoke coverage for generated `AGENTS.md` and board README workflow
content.

### Acceptance
- Smoke renders a temporary consumer project using generic paths.
- Generated `AGENTS.md` and `openspec/board/README.md` are checked for
  lifecycle, role model, fresh review gate and board finalization guidance.
- The smoke is included in the relevant verification floor for future template
  workflow changes.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-12-add-bootstrap-workflow-guidance-smoke/`

## Log
- 2026-07-12T13:15:07Z card created from post-delivery retrospective
  improvement list.
- 2026-07-12T13:28:00Z fast-forward planning created five OpenSpec changes and
  moved the card to `2.todo`.
- 2026-07-12T13:50:00Z delivery implemented helpers, skills, docs, CI smoke,
  specs and verification; archived all five OpenSpec changes; moved card to
  `3.inprogress` for independent review.
- 2026-07-12T13:56:00Z independent review returned `no-go` because default
  public-surface scan did not cover `openspec/changes/archive`; fixed scanner
  default roots, added self-test coverage for archived leaks and verified
  archive scan passes.
- 2026-07-12T14:05:10Z publish finalized card into `4.done` with commit `82e6b3e4c70e0a33db55be284458642f05496d76` and push status `pending`.

