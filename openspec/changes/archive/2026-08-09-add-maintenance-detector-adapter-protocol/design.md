## Context

The deterministic scan change covers ChangeRail-owned catalog, link, generated
freshness and active-reference detectors. Consumer architecture and instruction
checks remain project-specific: Java projects may use ArchUnit, other projects
may use different native checks, and ChangeRail core must not embed those
language-specific engines.

## Goals / Non-Goals

**Goals:**
- Add a generic adapter detector protocol configured through maintenance policy.
- Invoke adapters as argv arrays with `shell=False`, repository cwd and bounded
  timeout.
- Normalize adapter findings into the same detector-result/report contract used
  by core detectors.
- Treat adapter failure, timeout, invalid JSON and unsafe paths as detector
  errors that cannot produce a green architecture result.
- Provide generic fixtures without adding language analyzer runtime
  dependencies.

**Non-Goals:**
- Do not ship ArchUnit, ESLint, mypy or another analyzer as a ChangeRail core
  dependency.
- Do not define the instruction-budget producer contract from series `050`.
- Do not allow adapters to mutate repository state as part of maintenance scan.

## Decisions

- **Adapters are argv arrays.** Policy stores executable and arguments as a JSON
  array/YAML sequence. The scanner calls `subprocess.run(..., shell=False)` from
  repository root and applies timeout consistently.
- **One adapter output shape.** Adapter stdout is a single JSON document with
  findings that map to `changerail.maintenance-detector-result.v1`. Any other
  stdout shape is invalid adapter output.
- **Detector errors are separate from findings.** A failed process, timeout,
  invalid JSON or path escape records a detector error result. It is not
  interpreted as "no architecture findings".
- **Path normalization stays in ChangeRail core.** Adapter-provided paths are
  normalized with the same repository-relative safe-path helper as catalog and
  policy paths. Unsafe paths become detector errors.
- **Fixtures use tiny Python adapters.** Smoke tests create disposable adapter
  scripts that emit valid findings, invalid JSON, sleep past timeout and emit
  unsafe paths. These fixtures prove protocol behavior without adding external
  analyzers.

## Risks / Trade-offs

- **Adapters may be slow or flaky** -> Timeout is mandatory and timeout results
  fail closed as detector errors.
- **Adapter output can overfit to one language** -> Contract fields remain
  generic: detector id, severity, code, path, message and evidence details.
- **Consumer adapter mutation is hard to prove** -> Scan verifies no-mutation at
  the repository level for fixture adapters and documents adapters as read-only
  commands.
