## Context

Фаза 6 дорожной карты требует превратить OPSX из always-latest checkout в
поддерживаемую технологию. Риск already documented в архитектуре: `git pull` в
`/opt/opsx` сразу меняет behavior подключенных consumer projects. Для этого
нужны version marker, changelog, compatibility notes и migration notes.

## Decisions

- `VERSION` становится коротким machine-readable marker текущей версии. На
  bootstrap stage OPSX начинает с `0.1.0`, чтобы semver явно показывал pre-1.0
  compatibility status.
- `CHANGELOG.md` использует Keep-a-Changelog-like структуру с `Unreleased` и
  версиями. Breaking changes маркируются строками, начинающимися с
  `BREAKING:`.
- `docs/release-discipline.md` описывает semver policy, release checklist и
  update ritual для `/opt/opsx`.
- `docs/compatibility.md` фиксирует текущую support policy для Codex CLI,
  Claude Code и OpenSpec CLI. OpenSpec CLI pin читается из `bin/openspec`.
- `docs/migration-guide.md` фиксирует migration notes между версиями. Для
  начальной версии записывается `initial public baseline`.
- README и architecture docs ссылаются на новые release docs вместо
  формулировки "planned".

## Non-Goals

- Не создавать git tag или release artifact.
- Не менять `bin/openspec` pin.
- Не добавлять CI workflow; это делает зависимый change
  `add-release-ci-gate`.

## Public Safety

Документы используют только generic paths: `/opt/opsx`,
`/opt/example-project`, `/opt/example-a`, `/opt/example-b`. Migration notes не
должны ссылаться на private workspace inventory.
