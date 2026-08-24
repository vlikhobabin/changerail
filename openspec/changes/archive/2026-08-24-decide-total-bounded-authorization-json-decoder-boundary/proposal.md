## Why

Independent cycle 3 отклонил неопубликованный authorization payload после
исчерпания same-card rescue budget `2/2`: legal JSON integer из 4301 цифры
доходит до conversion, outcome/detail зависит от CPython
`PYTHONINTMAXSTRDIGITS`. Escalation также обнаружил permissive
`NaN`/`Infinity` и отдельный unrestricted inline `json.loads`, способный
выпустить `RecursionError`. Published type-safe classification decision не
задает total resource/numeric boundary для этих двух decoder roles.

Нужна отдельная decision-only investigation до любой новой implementation или
publication попытки. Failed payload остается forensic-only и не переносится в
clean worktree.

## What Changes

- Фиксируется один strict JSON decoder contract для source
  `Investigation authorization` values и inline
  `Published investigation authorization` references.
- Numeric tokens остаются parser-owned lexemes до role validation; maximum 64
  ASCII characters устраняет зависимость от `PYTHONINTMAXSTRDIGITS`, а
  `NaN`/`Infinity`/`-Infinity` получают stable strict rejection.
- Фиксируются exact universal ceilings: 4096 code points, 255 lexical tokens и
  depth 16 на value; 16 exact fields, 16384 code points и 1020 tokens на один
  Markdown document.
- Фиксируется complete single-pass first-failure order: field count, aggregate
  characters, per-value characters, strict constants, syntax, numeric length,
  depth, per-value tokens, aggregate tokens; same-event collision fixtures
  делают exact detail observable для обеих roles и обоих environments.
- Фиксируются exact decoder details, source-versus-inline cardinality,
  pair/identity behavior и zero-dispatch fail-closed oracle.
- Future production RED/GREEN contract требует одинаковую connected matrix при
  `PYTHONINTMAXSTRDIGITS=640` и `0`, existing phase-routed matrix, full smoke,
  release baseline, strict OpenSpec, source classification, compile/Ruff,
  public scan и diff checks.
- Выбирается единственная replacement identity
  `authorize-total-bounded-phase-routed-resume-integrity-payload`, но card и
  downstream successor не создаются.
- Investigation остается decision-only: planning меняет только card и один
  active OpenSpec change; apply позднее синхронизирует один main requirement и
  архивирует change без parser/test/schema/runtime edits.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-contracts`: добавить normative decision для общего strict,
  total и bounded authorization JSON decoder, dual-role matrix и exact clean
  replacement authorization lineage.

## Impact

Planning impact ограничен новой todo card и
`openspec/changes/decide-total-bounded-authorization-json-decoder-boundary/`.
Apply-time impact ограничен sync одного delta requirement, archive и card
metadata. Public methodology, skills, slash commands, templates, bootstrap,
schemas, production scripts, tests, CLI и runtime behavior не меняются.

Поздняя отдельная implementation card будет владеть parser и connected smoke в
`scripts/changerail_review_preflight.py` и
`scripts/smoke-review-preflight.py`. Она не может быть создана до publication
этой investigation и не может использовать rejected payload как authority.
