## Context

The filesystem MCP server was launched as
`@modelcontextprotocol/server-filesystem` without an exact version. Context7 is
already exact-version pinned, but no tracked integrity metadata documents the
expected package tarball. CI uses mutable major action tags.

## Goals / Non-Goals

**Goals:**
- Ensure every automatically executed npm MCP package in tracked config has an
  exact version.
- Track package integrity metadata in the repository for audit and update
  review.
- Ensure CI action references are immutable commit SHAs with human-readable
  version comments.

**Non-Goals:**
- Do not vendor npm tarballs.
- Do not replace the MCP server implementation.
- Do not introduce private package registries.

## Decisions

- Add root `mcp-npm-lock.json` as the lightweight integrity lock for MCP npm
  packages used by ChangeRail config and consumer templates.
- Keep `npx -y` invocation style for compatibility, but require the package
  argument to include an exact version and match the tracked lock metadata.
- Update `bin/verify-project` to inspect generated `.mcp.json` and
  `.codex/config.toml` package args and fail on unpinned or unlocked MCP npm
  packages.
- Pin `actions/checkout` and `actions/setup-node` by commit SHA in the workflow
  and keep comments naming the corresponding major version tag.

## Risks / Trade-offs

- [Risk] A tracked integrity lock documents expected package metadata but `npx`
  still delegates installation to npm. Mitigation: release docs require trusted
  setup/update review and verifier prevents accidental floating package args.
- [Risk] Action SHAs are less readable than tags. Mitigation: comments carry
  version labels and docs describe the update command.
