## Context

`scripts/changerail_delivery_manifest.py` derives `workspace.repository` from
`remote.origin.url`. Git remotes may include `https://user:password@host/repo`,
token-like query values or SSH userinfo. `bin/changerail-delivery-runner`
currently writes the submitted `--connectivity-url` and raw exception text into
structured preflight checks.

## Goals / Non-Goals

**Goals:**
- Preserve enough repository and endpoint metadata for operators to identify
  the source being checked.
- Remove URL userinfo, passwords, tokens, sensitive query values and fragments
  before structured runtime writes.
- Avoid printing raw submitted connectivity URLs in pass or fail diagnostics.

**Non-Goals:**
- Do not claim raw child stdout/stderr logs are sanitized.
- Do not add a secret vault or credential classifier.
- Do not change runtime schema ids.

## Decisions

- Add small sanitizer helpers near the runtime writers rather than broad global
  logging hooks. This keeps redaction close to the fields being persisted.
- For URL remotes, keep scheme, host, optional port and path; drop userinfo,
  query and fragment. For SCP-style SSH remotes, keep host and repository path
  while omitting the SSH username.
- Connectivity diagnostics store `scheme`, `host`, optional `port`, HTTP
  status for success and exception class for failure. The raw URL and raw
  exception message are not persisted because both may echo sensitive input.
- Docs explicitly state that runner child logs remain raw runtime evidence and
  must not be published as public artifacts.

## Risks / Trade-offs

- [Risk] Dropping URL query values can remove useful diagnostics. Mitigation:
  retain host/scheme/status and require operators to inspect private local
  context when detailed debugging is needed.
- [Risk] SSH username redaction can make unusual remotes less recognizable.
  Mitigation: host and repository path remain available.
