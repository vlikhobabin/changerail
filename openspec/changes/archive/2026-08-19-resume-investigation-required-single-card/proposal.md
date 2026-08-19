## Why

Single-card `resume` сейчас поддерживает только remote publish-target preflight
failure. После `investigation_required` оператор может опубликовать требуемые
investigation и authorization sources, но runner не умеет возобновить исходный
retained dirty payload без unsafe clean-tree обхода.

## What Changes

- Добавить explicit single-card resume path для prior status с
  `terminal_reason: investigation_required`.
- Принимать только совпадающие prior card, workspace и retained-payload
  identity, затем заново запускать deterministic preflight.
- Требовать clean tracked `HEAD` artifacts для published investigation и
  bounded authorization chain перед продолжением review/publish.
- Сохранять dirty working tree как review target; checkpoint commit, stash,
  branch name или prose assertion не становятся review evidence.
- Fail closed со stable machine reasons для stale/missing authorization,
  relation mismatch, wrong card/workspace и fingerprint drift.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-delivery-runner`: single-card `resume` can continue an authorized
  `investigation_required` retained payload.
- `changerail-contracts`: deterministic preflight and delivery-run status
  contracts cover retained-payload resume validation.

## Impact

- `bin/changerail-delivery-runner`
- `schemas/changerail-delivery-run.schema.json`
- `schemas/changerail-review-preflight-result.schema.json`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `openspec/specs/changerail-contracts/spec.md`
- Focused synthetic smokes for successful and adversarial single-card resume
