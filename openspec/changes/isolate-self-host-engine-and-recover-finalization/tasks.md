## 1. engine-identity

- [ ] 1.1 Материализовать immutable engine snapshot и полный execution inventory.
- [ ] 1.2 Разделить engine identity и project payload identity в runner и launchers.
- [ ] 1.3 Добавить fail-closed проверки drift profile, launcher, symlink и engine.

## 2. self-host-recovery-lifecycle

- [ ] 2.1 Реализовать prepare с predecessor inventory, accepted plan и corrective diff.
- [ ] 2.2 Реализовать atomic apply одного successor под project lock.
- [ ] 2.3 Реализовать reconcile/retry без изменения старого run и accounting.
- [ ] 2.4 Продолжить successor с finalize через обычные review/archive/final/publish gates.

## 3. verification-and-docs

- [ ] 3.1 Добавить регрессии race/crash/drift/live-process и boundary cases.
- [ ] 3.2 Добавить synthetic lifecycle с локальным remote и retained evidence.
- [ ] 3.3 Обновить русские runbook и distribution attach guidance.
- [ ] 3.4 Выполнить strict OpenSpec, focused/full tests, Ruff и diff-check.
