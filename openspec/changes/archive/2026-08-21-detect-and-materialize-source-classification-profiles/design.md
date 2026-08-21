## Context

Profile contract предоставляет validated classification data, path-only
detection signals, checksum и merge semantics. Current setup guidance упоминает
только ручной `.changerail/source-classification.yaml`; ни одна command не
находит candidate profiles и не создает file. Ordinary review preflight не
должен выполнять detection, иначе payload сможет изменить rules собственной
оценки.

## Goals / Non-Goals

**Goals:**

- Add one cross-platform Python-backed helper with `detect` and `materialize`.
- Make detection read-only, deterministic and based on pre-change tracked tree
  by default.
- Require explicit selected profiles and preview before any write.
- Produce schema-valid idempotent classification/provenance.
- Prove unaccepted candidates never affect current risk.

**Non-Goals:**

- Не auto-detect/materialize во время review/delivery/preflight.
- Не overwrite/migrate отличающийся existing file.
- Не commit generated file автоматически.
- Не execute language/domain analyzers or inspect source contents.

## Decisions

1. **New helper surface:** `bin/changerail-source-classification` with JSON/text
   modes and `detect`, `materialize`, later `check`. Linux wrapper calls pinned
   runtime Python; Windows `.cmd` parity and bootstrap wiring follow existing
   helper conventions.

2. **Detection defaults to tracked `HEAD`.** Helper enumerates normalized paths
   with `git ls-tree -r --name-only HEAD`, not working tree. Explicit
   `--snapshot <tree-ish>` resolves to a Git tree and records its object id.
   Unresolvable/non-tree inputs fail. This prevents the reviewed payload from
   adding its own marker and changing classification mid-review.

3. **Confidence is deterministic and bounded.** For each profile, match required
   signals and sum matched/total weights into integer score; required miss makes
   candidate ineligible. Thresholds map to `low`, `medium`, `high`; ties and
   overlapping profile results populate `ambiguities`. Output includes matched
   signal ids/patterns, never file contents.

4. **Detection sources are explicit.** Built-in registry loads by default.
   `--profile-file` may add local integration profiles after schema/checksum
   validation. Output source is bounded kind/id/version/checksum and omits
   machine-absolute input path. Detection never writes any file.

5. **Materialization has preview-first mutation.** Operator passes one or more
   exact `--profile <id>@<version>` and/or validated `--profile-file`. Default
   invocation returns schema-valid plan and unified semantic summary without
   writing. `--write` applies only that preview-equivalent selection. There is
   no `--force` overwrite.

6. **Existing file behavior is deterministic.** If file absent, `--write`
   atomically creates final canonical YAML plus provenance. If byte/semantic
   content already matches, command is successful no-op. Any differing existing
   file produces bounded diff (rules/roots/measure/provenance only) and exits
   non-zero with explicit migration-required status.

7. **Risk changes only after tracked project policy exists.** Candidate report
   is ignored/advisory input. Existing review preflight still reads only
   `.changerail/source-classification.yaml`. Focused test compares same payload
   before detection, after detection and after materialization.

## Risks / Trade-offs

- [HEAD unavailable in new repo] -> detection fails with explicit snapshot
  diagnostic, not working-tree fallback.
- [Candidate confidence is imperfect] -> user must explicitly select; score has
  no risk authority.
- [Preview/write race] -> write revalidates snapshot/profile checksums and target
  absence/match before atomic replace.
- [YAML formatting differs] -> semantic canonicalization defines idempotency;
  existing different file is not reformatted silently.

## Migration Plan

1. Add helper implementation and Linux/Windows wrappers.
2. Add detect JSON schema/output fixtures.
3. Add preview/write/idempotence/conflict fixtures.
4. Wire helper into bootstrap/verify inventory without implicit execution.
5. Rollback removes helper; materialized files remain valid current policy.

## Open Questions

- none
