## Why

Delivery manifest derivation является boundary для staging proposal в
review-gated publish. Текущая реализация разбирала human-readable git status и
могла расширять untracked directory scope, из-за чего valid repository paths
записывались неверно, а unrelated files могли попасть в proposed staging.

## What Changes

- Выводить manifest file operations из NUL-safe git status data вместо
  line-oriented porcelain text.
- Сохранять точные repository-relative paths для add, modify, delete и rename,
  включая spaces, quotes, Unicode и literal ` -> ` в filenames.
- Разворачивать untracked directories до точных untracked files или
  консервативно отклонять non-file paths, если их нельзя безопасно представить.
- Добавить focused smoke coverage для tracked paths со spaces, rename/delete,
  Unicode paths, literal arrow text и mixed pre-existing dirty state.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-contracts`: requirements для delivery manifest derivation и
  staging-plan ужесточены: нужны byte-safe exact paths и отказ от
  directory-wide scope.

## Impact

- `scripts/changerail_delivery_manifest.py`
- `scripts/smoke-delivery-manifest-derive.py`
- `docs/changerail-contracts.md`
- `skills/changerail-do/references/changerail-delivery-manifest.md`
- `openspec/specs/changerail-contracts/spec.md`
