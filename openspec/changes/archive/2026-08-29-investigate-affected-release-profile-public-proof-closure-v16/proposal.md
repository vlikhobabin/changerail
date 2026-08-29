## Why

Terminal affected v15 исчерпал repair budget и оставил пять связанных blockers:
разделённую typed truth, поздний runtime admission, неполные origin ledgers,
monkeypatched selector proof, sample scheduler matrix и незамкнутый execution
oracle. Продолжение того же payload запрещено.

## What Changes

- Публикуется docs-only v16 simplification decision от safe authorization v15.
- Один typed registry становится production truth, а независимые fixture maps
  сравниваются с реально извлечёнными operands.
- Runtime/task-root proof выполняется до Git; tracing и public pure boundaries
  заменяют private helper/self-report evidence.
- Real Git fixtures, complete scheduler matrix и closed runner/profile/
  scheduler/broker graph становятся обязательными.
- Exact CI и остальные закрытые accumulated contracts сохраняются.

## Capabilities

### Modified Capabilities
- `changerail-release-ci`: задаёт clean v16 proof/admission successor boundary.

## Impact

Только board/OpenSpec/release-CI docs. Executable successors, certification и
prohibited runtime evidence отсутствуют.
