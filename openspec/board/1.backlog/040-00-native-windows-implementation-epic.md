# Серия 040: Реализация native Windows support

## Status
1.backlog

## Owner
ChangeRail core + operator

## OpenSpec Stage
epic

## Series
`040-native-windows-implementation`

## Series Index
`00`

## Planning State
refreshed after `030-03`; executable cards remain backlog until individual
readiness

## Delivery Mode
coordination-only; не запускать `$chrl-deliver` для этой epic-карточки

## Source
- `030-03-freeze-native-windows-architecture`: `.cmd` native runtime default,
  generated project-local Windows wiring default, bounded symlink/junction
  fallbacks, shared bootstrap/verify/drift ownership model and mandatory test
  matrix.
- Обязательное product решение о native Windows support.

## Summary
Реализовать выбранную в `030-03` native Windows architecture: tracked `.cmd`
entrypoints, generated-copy wiring backend, fail-closed verification/drift/Git
safety, automated two-host smoke and final clean-clone end-to-end proof.

## Entry Gate
- Серия `030-native-windows-discovery` завершена и опубликована.
- Architecture decision и test matrix из `030-03` приняты.
- Эта epic и все series cards переписаны против фактических research results.
- До выполнения gate ни одна `040-*` story не переводится в `2.todo`.

## Common Constraints
- Native Windows является supported surface, WSL остается отдельным environment.
- `.cmd` wrappers являются native Windows command default; direct extensionless
  POSIX wrappers и implicit Bash не являются supported native defaults.
- Generated project-local copies являются Windows wiring default.
- Symlink mode требует explicit operator opt-in и доказанной
  Developer Mode/privilege capability.
- Junction mode является explicit compatibility fallback с link-aware cleanup и
  Git-safety evidence.
- Bootstrap, verify, drift, refresh, upgrade и cleanup используют одну wiring
  classification и один generated ownership model.
- Git не должен случайно добавлять ChangeRail source, runtime state или
  credentials через generated, symlink или junction paths.
- Command construction безопасно обрабатывает spaces, non-ASCII paths and
  untrusted repository content.
- Live-host evidence sanitized; credentials и host identities ignored.

## Series Cards
1. `040-01-add-windows-runtime-entrypoints.md`
2. `040-02-add-windows-wiring-backend.md`
3. `040-03-add-windows-verification-and-git-safety.md`
4. `040-04-add-windows-automated-smoke.md`
5. `040-05-prove-native-windows-end-to-end.md`

## Exit Gate
- Bootstrap и verify проходят на обоих Windows hosts из clean disposable clone
  through generated-copy default, or support claim records an explicit blocker.
- Skill/command discovery подтвержден на supported Windows agent surfaces.
- Git safety и drift checks подтверждены до и после ChangeRail update.
- Full release baseline остается green on the primary Linux environment.
- Compatibility и migration docs отражают реальную support matrix.

## Related
- `openspec/board/1.backlog/030-00-native-windows-discovery-epic.md`
- `openspec/board/3.inprogress/030-03-freeze-native-windows-architecture.md`
- `docs/compatibility.md`
- `docs/wiring-discovery.md`
- `docs/migration-guide.md`
- `openspec/specs/changerail-windows-native-architecture/spec.md`

## Result
series refreshed against `030-03`; implementation not started

## Next
- После publish `030-03` подготовить `040-01` к delivery через
  `$changerail-ff openspec/board/1.backlog/040-01-add-windows-runtime-entrypoints.md`.

## Log
- 2026-08-01T15:07:29Z provisional epic создана отдельно от discovery series.
- 2026-08-02T07:27:00Z epic refreshed after `030-03`: selected `.cmd`
  entrypoints and generated-copy Windows wiring default; executable cards
  remain in `1.backlog`.
