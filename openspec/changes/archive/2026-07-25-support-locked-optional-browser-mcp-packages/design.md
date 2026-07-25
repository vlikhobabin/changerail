## Context

ChangeRail already treats automatically executed npm MCP packages as a
supply-chain gate: generated consumer config must use exact versions, every
package/version must be present in `mcp-npm-lock.json`, and trusted setup checks
compare tracked SRI values with npm registry metadata. Consumers can still add
optional browser MCP tooling for local workflows, but those packages need the
same lock discipline as default MCP packages.

## Goals / Non-Goals

**Goals:**
- Preserve fail-closed validation for unpinned, unlocked and integrity-mismatched
  MCP npm packages.
- Support exact package pins when `npx` receives the package as the direct
  executable package argument or through standard `--package` forms.
- Document the two approved optional browser package pins and how maintainers
  update them through trusted npm lookups.

**Non-Goals:**
- Do not upgrade browser MCP packages beyond `@playwright/mcp@0.0.68` and
  `chrome-devtools-mcp@0.20.3`.
- Do not add browser MCP packages to root ChangeRail config or generated
  consumer templates.
- Do not relax the integrity lock requirement for optional packages.

## Decisions

- Extend `mcp-npm-lock.json` with exact entries for
  `@playwright/mcp@0.0.68` and `chrome-devtools-mcp@0.20.3`, using `source:
  npm` and SRI `dist.integrity` values from trusted `npm view` lookups.
- Keep `bin/verify-project` package discovery argument-based. It should inspect
  each configured command argument list, identify `npx` package references in
  direct and `--package` forms, and feed the same exact-version, lock-presence
  and registry-integrity validator for all discovered packages.
- Add smoke fixtures that render consumer-local `.mcp.json` variants rather than
  modifying default templates, so optional browser tooling stays opt-in.
- Put update guidance in compatibility and release discipline docs: upgrading or
  adding optional executable MCP packages requires recording exact pins,
  refreshing lock metadata with `npm view`, and running verifier smoke and
  release gates.

## Risks / Trade-offs

- [Risk] `npx` supports many option permutations. Mitigation: cover the standard
  forms named in the card and keep fail-closed behavior for discovered npm MCP
  package references.
- [Risk] Optional packages could be mistaken for default bootstrap surface.
  Mitigation: smoke and review check that root config and `templates/project/*`
  remain free of browser MCP entries.
- [Risk] Registry metadata can change due to package republish or registry
  issues. Mitigation: trusted setup verification compares tracked SRI against
  current npm registry metadata before release.
