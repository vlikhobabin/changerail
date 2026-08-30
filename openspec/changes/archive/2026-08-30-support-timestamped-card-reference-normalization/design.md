## Context

The authorization matcher intentionally accepts only complete backticked bare,
filename or canonical board-path references. Its shared id fragment is
lowercase-only, but some consumer boards require sortable UTC prefixes such as
`2026-08-30T09-30-11Z-...`. These are exact card ids, not fuzzy prose, and the
current regex makes a valid authorization chain impossible to express.

## Goals / Non-Goals

**Goals:**

- Accept the existing lowercase slug grammar or one exact UTC
  `YYYY-MM-DDTHH-MM-SSZ-<lowercase-slug>` grammar.
- Apply the same bounded alternative to bare, filename and canonical board-path
  references.
- Prove both the matcher and complete published authorization chain.

**Non-Goals:**

- Accept arbitrary uppercase or mixed-case ids.
- Change card discovery, filenames, authorization JSON fields, risk routing or
  filesystem trust.

## Decisions

1. Add a dedicated timestamped reference-id grammar beside the existing
   lowercase `CARD_ID_RE`.

   The prefix has fixed digit groups plus literal uppercase `T` and `Z`; the
   suffix remains the existing lowercase slug grammar. The three reference
   regexes use the union, while other card-id consumers retain their current
   contract. After that lexical match, the timestamp prefix is parsed as a real
   UTC calendar/time value so impossible dates, out-of-range times and year
   `0000` remain non-matches.

2. Test the behavior source and the authorization consumer.

   Matcher assertions provide narrow negative cases. A synthetic repository
   with timestamped investigation, authorization and successor cards proves
   that exact tracked `HEAD` identity, reciprocal relations and preflight
   routing work together.

## Risks / Trade-offs

- **Over-broad mixed-case admission** → keep uppercase characters legal only at
  the two fixed UTC separators and assert arbitrary uppercase ids fail.
- **A matcher-only false green** → retain the end-to-end authorization-chain
  smoke through the public preflight command.
