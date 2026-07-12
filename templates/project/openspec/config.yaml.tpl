schema: spec-driven

context: |
  Repository: {{PROJECT_PATH}}
  Project: {{PROJECT_NAME}}
  Kind: {{PROJECT_KIND}}

  This project is a ChangeRail consumer. Reusable ChangeRail methodology, skills, command
  wrappers, schemas and helper wrappers are sourced from {{CHANGERAIL_ROOT}}.
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
