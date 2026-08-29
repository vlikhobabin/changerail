## Why

Terminal affected-profile v14 сохранил два blocker после единственной repair:
expected executable origin всё ещё выводился из live `PATH` при import, а
focused proof не различал scheduler aliases и потерю selector operands. Policy
ChangeRail требует новой clean investigation до следующего executable payload.

## What Changes

- Зафиксировать source-authored canonical origin policy, которая вычисляет
  expected targets независимо от live `PATH` и отклоняет usable fake,
  существующий до import.
- Определить semantic AST-mutant contract без marker-only uniqueness, reused
  edits, считаемых distinct mutants, early-return masking или counts-as-evidence.
- Замкнуть scheduler import/call ownership oracle против aliases, wrappers,
  dynamic dispatch и дополнительных execution surfaces.
- Сделать four-stream selector oracle exact и owner-discriminating для A/M/D и
  обоих R/C operands.
- Зафиксировать отдельный authorization и clean implementation v15 перед
  единственной final certification.
- Сохранить terminal v14 как forensic-only; production, tests и runtime в этой
  investigation не изменяются.

## Capabilities

### New Capabilities

- none.

### Modified Capabilities

- `changerail-release-ci`: добавить нормативную v15 investigation boundary для
  pre-import origin identity и discriminating source-connected proof.

## Impact

Change является docs-only и затрагивает card, same-slug OpenSpec artifacts и
накопленный `openspec/specs/changerail-release-ci/spec.md`. Consumer code,
dependencies, production scripts, tests, CI и runtime state не изменяются.
