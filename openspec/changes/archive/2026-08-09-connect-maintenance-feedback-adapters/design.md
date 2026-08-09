## Context

`bin/changerail-maintenance scan` уже умеет запускать generic detector
adapters, которые печатают один schema-valid
`changerail.maintenance-detector-result.v1`. Review-cycle histories and
delivery-run statuses are structured runtime records, but today they cannot be
fed back into that lifecycle without ad hoc scripts or prose scraping.

The existing frozen contracts stay authoritative:

- review histories use `changerail.review-cycle-history.v1`;
- delivery runs use `changerail.delivery-run.v1`;
- maintenance adapters use `changerail.maintenance-detector-result.v1`.

## Goals / Non-Goals

**Goals:**
- Add a read-only `feedback` command that validates explicit input paths and
  emits one detector result for a declared adapter id.
- Preserve source record, cycle/outcome metadata, original review finding id,
  severity and safe affected repository-relative paths.
- Treat malformed, unsafe, legacy or incomplete records as detector errors.
- Reuse existing lifecycle identity and board dedup behavior after feedback is
  normalized into detector findings.

**Non-Goals:**
- Do not change review verdict, review history, delivery run or delivery
  metrics schema ids.
- Do not parse stdout, stderr, logs or human diagnostics for control flow.
- Do not create cards, commits, comments, PRs or external mutations.
- Do not implement consumer-specific retrospective heuristics in ChangeRail
  core.

## Decisions

1. `feedback` emits adapter output directly.

   The command shape is:

   ```text
   bin/changerail-maintenance feedback --adapter-id <id> \
     [--review-history <path>]... [--delivery-run <path>]... \
     [--detector-result <path>]... --json
   ```

   The output id is `adapter-<id>`, matching the existing scan adapter boundary.
   Alternative considered: a new feedback-report schema. That would add another
   lifecycle normalization path for the same finding semantics, so the adapter
   result stays the boundary.

2. Review findings are normalized without copying review prose.

   Each `finding_details` entry becomes one or more detector findings. The
   generic finding message identifies the source cycle and original id; summary
   and detail prose are not copied into the detector result. The evidence object
   carries scalar source metadata such as `source_record`, `review_cycle` and
   `original_finding_id`. A finding with multiple safe paths becomes one finding
   per path so lifecycle identity includes both original id and affected subject.

3. Blocked delivery runs require structured terminal state.

   A delivery-run record creates a finding only when both `result` and
   `terminal_outcome` are `BLOCKED` and `terminal_reason` is present. Other valid
   terminal records do not create findings. A blocked record without a structured
   reason becomes an `unsupported_delivery_run` detector error.

4. External producer input is schema-valid detector output.

   `--detector-result` validates producer output with the existing detector
   schema, normalizes safe paths and merges findings/errors into the command
   result. This keeps external producer interoperability at the existing adapter
   boundary.

## Risks / Trade-offs

- [Risk] Generic feedback messages are less descriptive than review prose.
  Mitigation: source record, cycle and original id are retained so an operator
  can inspect the original runtime evidence when needed.
- [Risk] Review findings with no affected path have weaker dedup subjects.
  Mitigation: original finding id and source/cycle metadata remain in identity
  evidence; tests cover separate finding ids.
- [Risk] Mixed input can be partially useful and partially invalid.
  Mitigation: any invalid record makes the detector result `error` while
  retaining valid findings for audit visibility.

## Migration Plan

No migration is required. Existing runtime records remain readable as explicit
input paths, and existing scan/report behavior is unchanged unless an operator
or configured adapter invokes `feedback`.

## Open Questions

- none
