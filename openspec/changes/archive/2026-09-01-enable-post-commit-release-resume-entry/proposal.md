## Why

После исчерпания двух same-card rescue первый stable release остается
заблокирован: текущие `$changerail-pub` и `$changerail-deliver` обещают
возобновить частично выполненную publication transaction, но новая invocation
обязательно применяет pre-commit freshness и dirty working-tree scope gates к
уже созданному clean payload commit. Нужен отдельный fail-closed entry route,
который сохраняет строгий initial publish и делает post-commit handoff
действительно возобновляемым.

## What Changes

- Добавить в существующие lifecycle skills явный `--resume-release` mode и
  взаимоисключающий routing normal/resume gates.
- Сохранить deterministic preflight, current-worktree verdict freshness,
  verification и working-tree/staged manifest reconciliation непосредственно
  перед первым staging в normal mode.
- Для resume mode запретить dirty/pre-commit вход и вместо current-worktree
  freshness доказать existing positive verdict, payload parent/tree lineage,
  clean card/workspace, committed diff parity с единым successor manifest и
  exact remote feature-branch identity.
- Продолжать tag/release/assets transaction с первого отсутствующего шага
  только после exact annotation/title/notes/assets identity checks; любой
  mismatch или недостаток evidence останавливает mutation.
- Добавить regression coverage, различающее normal и resume gate traces,
  interrupted-resume states и adversarial wrong states, и исправить stale
  archived design wording о повторном post-commit freshness/full-gate.
- Сохранить existing dirty release payload и два predecessor archives без
  дублирования; следующий delivery manifest охватывает их вместе с новым
  linked-rescue payload.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-skill-surface`: определить явный post-commit resume entry и
  детерминированный routing между `$changerail-pub` и `$changerail-deliver`.
- `changerail-release-discipline`: усилить fail-closed release continuation
  committed lineage/scope/remote proofs и разделением initial/resume gates.

## Impact

Затрагиваются canonical `changerail-pub`/`changerail-deliver` skill contracts,
delivery-manifest scope proof и его focused regression, release/skill-surface
OpenSpec requirements, durable release discipline и одна stale фраза в
archived release design. Consumer provider configuration, credentials,
execution target, schema ids, release asset contract, dependency pins и
mutation authority не меняются. `--resume-release` является режимом
существующей явно разрешенной `1.0.0` transaction, а не новым provider или
wire protocol.
