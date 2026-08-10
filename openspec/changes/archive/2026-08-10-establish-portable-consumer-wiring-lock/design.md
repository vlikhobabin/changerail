## Context

POSIX symlink target сейчас всегда вычисляется относительно link parent.
Generated Windows wiring имеет ownership manifest, но обычный POSIX consumer не
хранит intended ChangeRail source/version/path mode. Поэтому move/clean clone и
source update невозможно классифицировать как valid, drifted или project-owned.

## Goals / Non-Goals

**Goals:**
- сделать independent POSIX wiring clone-portable;
- ввести public schema для intended source и wiring policy;
- отделить broken wiring от source drift;
- разрешить bounded automatic repair в disposable/local checkout.

**Non-Goals:**
- объединять или менять frozen `changerail.generated-wiring.v1`;
- обновлять ChangeRail checkout автоматически;
- хранить absolute consumer/source paths или credentials в lock;
- разрешать arbitrary file replacement.

## Decisions

### POSIX path mode

`--wiring-path-mode absolute|relative` применяется только к symlink backend.
Default `absolute` указывает на resolved `--changerail-root` и соответствует
документированному independent-consumer contract. `relative` требует explicit
opt-in для layout, где consumer и ChangeRail перемещаются как единое дерево.

### Consumer lock

Tracked path: `openspec/changerail-consumer-lock.json`.
Public schema: `schemas/changerail-consumer-lock.schema.json`, id
`changerail.consumer-lock.v1`.

Lock содержит:
- ChangeRail `version` из `VERSION` и exact Git `revision`;
- canonical public source reference без credentials;
- wiring `platform`, `backend`, `path_mode` и known artifact inventory;
- selected project/surface/Codex profiles;
- `enforcement: advisory|strict`.

Lock не содержит resolved machine root. Strict/advisory generation требует
tracked clean ChangeRail source; explicit no-lock development mode сохраняет
legacy bootstrap path.

### Drift semantics

Verifier выдает отдельные checks для schema/intent, actual wiring и source
revision. Wiring mismatch всегда blocking. Source mismatch при `advisory`
становится non-blocking diagnostic, при `strict` — blocking failure.

### POSIX repair

`--refresh-wiring` читает lock и пересоздает только known symlink paths. Real
files/directories, scope escape, symlink parent escape и unrelated dirty state
останавливают операцию до mutation. Disposable CI checkout может использовать
тот же repair с другим runtime ChangeRail root; lock revision при этом не
меняется.

### Windows compatibility

Windows продолжает использовать `openspec/changerail-wiring.json` и
generated-copy default. Consumer lock может ссылаться на backend/revision, но
не заменяет digest ownership manifest.

## Risks / Trade-offs

- [Absolute links still require installed contract root] -> lock-driven repair
  делает relocation deterministic; relative mode остается explicit option.
- [Two manifests confuse ownership] -> consumer lock владеет intent/source,
  existing Windows manifest владеет generated artifact digests.
- [Dirty ChangeRail checkout cannot produce reproducible lock] -> fail closed
  для locked modes и explicit no-lock mode для development fixtures.

## Migration Plan

1. Добавить schema и contract smoke.
2. Добавить lock renderer/loader и POSIX path mode.
3. Расширить verifier/discovery/repair.
4. Добавить non-sibling clean-clone и negative fixtures.
5. Existing lockless consumers остаются на legacy compatibility path.

## Open Questions

- none
