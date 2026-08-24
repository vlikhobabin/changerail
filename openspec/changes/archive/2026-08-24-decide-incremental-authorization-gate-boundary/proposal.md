## Why

Неопубликованный `authorize-total-bounded-phase-routed-resume-integrity-payload`
исчерпал same-card rescue budget после двух independent `NO-GO`: field 17
читается до admission reject, а greedy numeric match заставляет исходный
4301-digit regression падать на character 4097 вместо numeric character 65.
Published decision `6e1cbfa` сохраняет правильные limits/details/order, но его
exclusive implementation identity больше нельзя repair-ить или публиковать.

## What Changes

- Фиксируется incremental exact-field extractor, который отклоняет 17th prefix
  до line-end/content access, trim, backtick normalization или span retention.
- Фиксируется incremental RFC 8259 numeric FSM без whole-value regex и без
  `int()`/`float()`/`Decimal()` conversion; 4301-digit rows отклоняются exact на
  numeric character 65 при `PYTHONINTMAXSTRDIGITS=640` и `0`.
- Уточняется nested exact delimiter contract для prohibited constants:
  end/whitespace/comma/`]`/`}` дают constant detail, suffix/malformed form дает
  generic syntax detail.
- Полностью сохраняются ceilings, stable details, first-failure order,
  pair-preserving role validation и zero-dispatch contract `6e1cbfa`.
- Исчерпанная identity получает decision-level `SUPERSEDED` без mutation ее
  worktree/history; выбирается exact clean lineage A->B->C->D->existing
  successor.
- B связывает A с C exact six-field object, ceiling 301, protocol false; D
  позднее связывает A с successor, ceiling 500, protocol true.
- Fast-forward остается decision-only: только todo card и один active change;
  downstream cards, code/tests, main spec, archive, verdict и publish absent.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-contracts`: добавить normative decision для incremental
  authorization admission/scanning boundary и clean superseding lineage.

## Impact

Planning impact ограничен
`openspec/board/2.todo/investigate-incremental-authorization-gate-boundary.md`
и `openspec/changes/decide-incremental-authorization-gate-boundary/`.
Apply-time impact позднее ограничен sync одного requirement, archive и card
metadata. Production parser, smoke/tests, schemas, runner, CLI/runtime docs,
main spec, forensic payload и downstream cards в этой фазе не меняются.

Public surface остается generic и не добавляет private data, credentials,
runtime reports или machine-specific forensic paths.
