## Context

`establish-repository-knowledge-contract` вводит schema-backed catalog/policy
loader. Второй change делает contract usable из shell и CI: maintainer должен
валидировать configured catalog и проверять deterministic generated index без
agent involvement.

В репозитории уже есть shared Python runtime wrappers (`bin/changerail-python`,
`.cmd` variants) и smoke coverage для POSIX/native Windows entrypoints. Новый
helper должен использовать тот же launch pattern и не обходить runtime selector.

## Goals / Non-Goals

**Goals:**
- Добавить POSIX и native Windows entrypoints для `changerail-maintenance`.
- Поддержать `validate-catalog` с default paths и explicit `--catalog` /
  `--policy` overrides.
- Поддержать `render-index --check|--write` со stable ordering и read-only
  default/check mode.
- Записать generated index только в configured generated index path.
- Добавить smoke tests для CLI validation, index idempotence, no-mutation check
  mode и wrapper presence.

**Non-Goals:**
- Не добавлять repository scan, findings baseline, scheduler integration или
  fix mode.
- Не запускать generators из `verify` или policy fields.
- Не делать `.changerail/maintenance.yaml` обязательным для existing consumers.

## Decisions

- **Single script command surface.** `scripts/changerail_maintenance.py`
  exposes subcommands while reusing `scripts/changerail_repository_knowledge.py`
  for loading, validation and rendering. Wrappers stay thin.
- **Read-only unless `--write`.** `render-index` renders expected content in
  memory; `--check` compares existing file and exits non-zero on drift;
  `--write` is the only mode that mutates the generated index path.
- **Generated index path comes from policy.** Default policy points to
  `.changerail/KNOWLEDGE.md`, and CLI overrides can point elsewhere, but
  semantic path validation still rejects absolute/traversal paths.
- **Stable ordering by normalized path.** Index rendering sorts records by
  normalized `path`, then `type`, then `status`, making repeated output
  idempotent and diff-friendly.
- **Dogfood as contract fixture.** ChangeRail tracks a minimal catalog for its
  own canonical docs and commits the generated index after `--write`.

## Risks / Trade-offs

- **Index format may need richer metadata later** -> MVP renders the contract
  fields needed for human navigation and can be extended with an additive
  schema change.
- **Windows smoke cannot execute `.cmd` on Linux** -> repo smoke verifies wrapper
  syntax/presence locally; native execution remains covered by the Windows
  smoke matrix.
- **Policy overrides can confuse consumers** -> CLI diagnostics report the exact
  catalog, policy and index paths being used without writing runtime state.
