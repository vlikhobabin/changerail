## Context

Репозиторий уже описывает OPSX как public source of truth для OpenSpec-driven
AI-assisted development. Следующий bootstrap step - отделить generic OPSX
methodology от repo-specific rules, чтобы consumer projects могли получать
stable methodology section без копирования private или local context.

## Goals / Non-Goals

**Goals:**
- Создать public-safe `AGENTS.shared.md` для reusable OPSX methodology.
- Держать consumer-facing rules generic и независимыми от domain-specific
  extension.
- Сохранить root `AGENTS.md` как policy для разработки самого `/opt/opsx`.
- Сделать результат пригодным для будущих `templates/project` и
  `verify-project` drift checks.

**Non-Goals:**
- Не мигрировать `opsx-*` skills или Claude slash commands в этом change.
- Не реализовывать `bootstrap-project` или `verify-project` в этом change.
- Не добавлять private workspace inventory, migration notes или domain-specific
  extension policy.

## Decisions

- `AGENTS.shared.md` является реальным tracked file в корне репозитория.
  Рассмотренная альтернатива: держать methodology только в architecture docs.
  Root file проще находить agents, templates и drift checks.
- Consumer projects в будущем по умолчанию получают generated section с
  hash/version marker. Рассмотренная альтернатива: только external link.
  Generated content надежнее для agents, которые не импортируют автоматически
  файлы вне repository.
- Root `AGENTS.md` остается repo-specific и не становится symlink или full copy
  shared file. Это оставляет public-safety и local verification rules явными для
  самого OPSX.

## Risks / Trade-offs

- Shared methodology может стать слишком широкой -> держать ее сфокусированной
  на workflow, boundaries и gates; domain-specific rules оставлять extensions.
- Generated sections могут drift-ить -> будущий `verify-project` должен
  сравнивать hash или canonical content с `AGENTS.shared.md`.
- Agents могут игнорировать external references -> templates должны встраивать
  shared section, а не полагаться только на link.

## Migration Plan

1. Добавить `AGENTS.shared.md`.
2. Обновить root `AGENTS.md` только если нужно прояснить split между shared и
   repo-specific правилами.
3. Проверить OpenSpec artifacts и baseline repo config.
4. Использовать shared file как input для будущих template и verification
   changes.

## Open Questions

- Точный generated-section marker format будет финализирован вместе с
  `templates/project` и `verify-project`.
