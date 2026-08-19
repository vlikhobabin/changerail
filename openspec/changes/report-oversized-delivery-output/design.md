## Context

Once runner status contains command output metadata, operators need a concise
view that explains which commands amplified output and how to remediate. The
metrics surface also needs to show output size alongside token usage while
preserving the existing rule that missing optional token fields are `unknown`.

## Goals / Non-Goals

**Goals:**
- Print sanitized top oversized commands in runner summaries.
- Expose output amplification metadata in delivery metrics text, JSON and CSV
  outputs where supported.
- Add synthetic smoke that proves byte accounting, bounded status size and no
  raw payload copy.
- Document the relationship between output bytes and cached/uncached token
  usage.

**Non-Goals:**
- Infer exact tokens from command bytes.
- Store private source excerpts in tracked docs or smoke fixtures.
- Remove ignored raw stdout/stderr evidence.
- Make oversized output alone a delivery failure.

## Decisions

1. Runner summary uses sanitized command labels. It may include executable,
   bounded argument preview, byte counts and remediation, but not raw output.
2. Metrics treats output bytes and token usage as separate dimensions. Output
   metadata can explain likely amplification even when usage is unavailable.
3. CSV gets stable columns with `unknown` for missing optional values, matching
   existing metrics semantics.
4. Synthetic smoke uses generated generic lines and checks status size. The
   fixture should fail if the raw oversized payload is copied into status.

## Risks / Trade-offs

- [Command label may still reveal sensitive arguments] -> Reuse existing
  sanitizer patterns and cap argument previews.
- [Metrics columns grow] -> Prefer a small stable set: oversized count, largest
  command bytes, top command label and threshold.
- [Byte counts do not equal token cost] -> Docs explicitly separate byte
  accounting from model-reported cached/uncached tokens.

## Migration Plan

Metrics remains compatible with records that lack output metadata by rendering
new values as `unknown`. Operator-facing summaries appear only for new runner
records that include oversized command data.

## Open Questions

- Should remediation text live in runner code, documentation, or both?
- Should JSON metrics expose the full bounded top-N list while CSV exposes only
  the largest command summary?
