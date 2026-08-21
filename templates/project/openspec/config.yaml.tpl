schema: spec-driven

context: |
  Repository: {{PROJECT_ROOT_LABEL}}
  Project: {{PROJECT_NAME}}
  Profile: {{PROJECT_PROFILE}}

  This project is a ChangeRail consumer. Reusable ChangeRail methodology, skills, command
  wrappers, schemas and helper wrappers are sourced from
  {{CHANGERAIL_ROOT_LABEL}}.
  Project-specific code, board cards, OpenSpec changes, runtime policy and
  verification remain local to this repository.

rules:
  proposal:
    - Describe whether the change affects project code, local ChangeRail wiring, docs,
      runtime policy or verification.
    - Keep public examples generic unless project owners explicitly document a
      private repository policy.
  specs:
    - Write requirements as observable project behavior.
    - Keep implementation details out of requirements unless they define a
      contract the project must preserve.
  design:
    - Explain affected files, migration choices and verification impact.
  tasks:
    - Include concrete verification commands.
    - Include public-safety scans when files could expose local data.

verification:
  profile: {{SURFACES_PROFILE}}
  # Optional tracked project-owned map, for example .changerail/verification-coverage.yaml.
  coverage_map: null
  surfaces:
    codex: {{CODEX_SURFACE_STATE}}
    claude: {{CLAUDE_SURFACE_STATE}}
    legacy_mcp: {{LEGACY_MCP_SURFACE_STATE}}
    legacy_artifacts: {{LEGACY_ARTIFACTS_SURFACE_STATE}}
  mandatory:
    targeted_openspec_validation: required
  baseline_debt: []

bootstrap:
  project_profile: {{PROJECT_PROFILE}}
  surfaces_profile: {{SURFACES_PROFILE}}
  codex_policy: {{CODEX_POLICY}}
