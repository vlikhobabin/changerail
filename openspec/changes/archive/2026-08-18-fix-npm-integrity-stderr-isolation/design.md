## Context

`npm view ... --json` has a machine-readable stdout contract, while npm may
emit warnings to stderr even when it exits successfully. Combining the streams
before JSON parsing violates that boundary.

## Decision

Use separate subprocess pipes. On exit code 0, parse only stdout. On failure,
join non-empty stdout and stderr for the existing operator diagnostic.

## Verification

The fake npm fixture emits the locked integrity to stdout and a warning to
stderr. The end-to-end verifier smoke must pass this case while retaining the
existing tampered-integrity failure case.
