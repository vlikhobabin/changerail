## Context

`scripts/public-surface-scan.py` already defines default public roots and
allowlists generic `/opt/changerail` and `/opt/example-*` paths. It does not
detect token-like assignments, home paths or leaks that were removed from the
current tree but remain in reachable history.

## Goals / Non-Goals

**Goals:**
- Detect common secret-bearing assignment patterns in current tracked files.
- Detect Linux, macOS and Windows home-directory paths.
- Support a documented `--history` mode over reachable git history.
- Redact secret values in scanner output.

**Non-Goals:**
- Do not replace specialized external secret scanners for release audits.
- Do not print full matched secret values.
- Do not scan ignored runtime files by default.

## Decisions

- Keep the scanner dependency-free Python so it remains usable in bootstrap
  and CI environments.
- Add typed finding kinds (`path`, `home-path`, `secret`) while preserving the
  existing JSON schema id.
- Redact secret finding values to `<redacted:secret>` and include only
  file/line/kind/message in normal output.
- Implement history scanning by walking reachable revisions and scanning text
  blobs through Git plumbing rather than printing raw `git grep` matches.

## Risks / Trade-offs

- [Risk] Heuristic secret detection may produce false positives. Mitigation:
  limit detection to assignment-like syntax and maintain explicit allowlists
  for placeholders and generic examples.
- [Risk] History scans are slower than current-tree scans. Mitigation: keep
  history mode explicit locally and run it as a documented release command or
  CI step.
