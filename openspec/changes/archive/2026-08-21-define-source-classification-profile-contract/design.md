## Context

`changerail.source-classification.v1` описывает конечные project-owned
`source_kinds`, production/non-production roots and measurement strategy.
`changerail_review_preflight.py` читает только
`.changerail/source-classification.yaml`; при его отсутствии используется
built-in common-language classifier. Contract не хранит происхождение правил и
не имеет reusable profile envelope или detection signals.

Profile должен быть data-only, одинаково валидироваться для built-in и
integration input и не становиться вторым runtime policy source. Для
воспроизводимости materialized classification должен помнить selected profile
identity/checksum, но preflight продолжает исполнять только конечные правила в
project file.

## Goals / Non-Goals

**Goals:**

- Определить versioned profile envelope с classification payload и bounded
  path-only detection signals.
- Дать canonical checksum и deterministic multi-profile merge.
- Поддержать built-in generic data и explicit local integration data одной
  схемой.
- Записать optional provenance/declared overrides в существующей classification
  без breaking migration.
- Fail closed на unsafe paths, executable/network fields и measurement
  conflicts.

**Non-Goals:**

- Не добавлять предметные платформы или их каталог names в generic core.
- Не выполнять profile code, commands, imports или network fetches.
- Не менять preflight risk от одного обнаруженного profile candidate.
- Не определять CLI mutation flow в этом change.

## Decisions

1. **Profile is a separate versioned data envelope.**
   `changerail.source-classification-profile.v1` содержит `id`, semantic
   `version`, optional description, `classification` payload compatible with
   `changerail.source-classification.v1` and bounded `detection.signals`.
   Встраивание profile metadata вокруг runtime file отвергнуто: интеграциям
   нужен reusable independent artifact, а project file должен оставаться
   конечной policy.

2. **Detection signals inspect repository names only.** Signals use normalized
   repository-relative glob plus positive integer weight and optional required
   flag. Нет regex over contents, shell command, URL, dynamic module или
   arbitrary expression. Это позволяет `git ls-tree` detection без чтения
   source bodies и без trusted code expansion.

3. **Checksum is derived, not self-declared.** Canonical SHA-256 считается по
   UTF-8 canonical JSON representation полного schema-valid profile with sorted
   object keys and preserved list order. Report formats it as `sha256:<hex>`.
   Checksum не является полем profile, поэтому нет self-reference; изменение
   content при том же id/version обнаруживается как immutable-version conflict.

4. **Built-in profiles are tracked data.** Generic profiles находятся под
   versioned ChangeRail data directory и проходят ту же schema/checksum
   validation. Local integration profile читается только по explicit CLI path;
   source report хранит kind `local-integration` and checksum, not an absolute
   machine path. Registry loading, entry points and remote catalogs запрещены.

5. **Merge preserves caller order but conflicts fail closed.** Selected profile
   list order записывается. Source-kind ids уникальны; equivalent duplicate
   rules deduplicate. Overlapping suffix/root rules with different `measure`,
   duplicate id with different content or conflicting non-production semantics
   block merge rather than last-writer-wins. Canonical output sorts rules/paths
   for reproducibility after conflict resolution.

6. **Existing classification gets optional provenance.** v1 schema добавляет
   `profile_provenance` with ordered `{id, version, checksum, source_kind}` and
   optional normalized override field paths. Top-level `source_kinds` and
   `non_production_roots` remain final effective rules and only runtime source
   for preflight. Existing files without provenance validate unchanged.

7. **Overrides declare intent, not duplicate values.** Provenance lists paths
   such as `source_kinds.<id>.production_roots`; actual value exists only in
   final classification. Later check compares profile baseline with final file:
   declared differing paths are project overrides, undeclared differences are
   drift.

## Risks / Trade-offs

- [Path-only detection has false positives] -> candidate confidence is advisory
  until explicit materialization.
- [Profile version mutates] -> same id/version with another checksum fails.
- [Merge overlap is hard] -> conservative conflict blocks instead of implicit
  precedence.
- [Provenance makes v1 richer] -> fields optional and existing loader ignores
  them after schema validation while using final rules exactly as before.

## Migration Plan

1. Add profile schema, canonical checksum helper and contract inventory.
2. Extend source-classification v1 with optional provenance.
3. Add generic built-in profile data and valid/invalid/conflict fixtures.
4. Detection/materialization follows in dependent change.
5. Rollback removes profile data/provenance writer; legacy project files remain
   valid and effective.

## Open Questions

- none
