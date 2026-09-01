## 1. Stable metadata

- [x] 1.1 Установить `VERSION=1.0.0`, добавить датированный `1.0.0` и новый
  пустой `Unreleased` в changelog без ложного dependency-pin claim.
- [x] 1.2 Добавить `0.5.0 -> 1.0.0` compatibility/migration/release notes с
  required actions, rollback и explicit native Windows caveat.
- [x] 1.3 Согласовать README/status и release discipline с final stable
  support/publication state, не включая deferred payloads.

## 2. Frozen candidate certification

- [x] 2.1 Создать isolated clone exact frozen candidate, ограничить heavy
  suites двумя CPUs и установить pinned `requirements-dev.txt` в clone-local
  virtual environment.
- [x] 2.2 Последовательно выполнить core и extended release suites на одном
  candidate, затем release CI smoke и current/history public scans.
- [x] 2.3 Выполнить применимые trusted-network npm integrity и CI action tag
  checks без изменения pins; сохранить public-safe ignored evidence.
- [x] 2.4 Выполнить source distribution reproducibility/checksum verification,
  config parsing, strict OpenSpec и whitespace gates на exact candidate.

## 3. Review and publication handoff

- [x] 3.1 Подготовить card/manifest concise evidence, sync specs и
  archive-ready handoff без tag, GitHub Release или tracked runtime state;
  фактический archive выполняет `changerail-do` после task completion.
- [x] 3.2 Зафиксировать обязательный fresh xhigh independent
  final-certification `GO` и запрет substantive edits после verdict;
  фактический verdict пишет только отдельная review phase.
- [x] 3.3 Зафиксировать post-GO explicit-manifest commit/push, annotated
  `v1.0.0`, reproducible assets, public GitHub Release и read-only proof;
  фактическую mutation выполняет только publish phase.
