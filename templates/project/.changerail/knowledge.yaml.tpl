schema: changerail.repository-knowledge.v1
records:
  - path: AGENTS.md
    status: active
    type: reference
    owner: "{{PROJECT_NAME}}"
    source_globs:
      - AGENTS.md
    verify:
      - bin/verify-project .
    review_after: null
    supersedes: []
  - path: openspec/board/README.md
    status: active
    type: reference
    owner: "{{PROJECT_NAME}}"
    source_globs:
      - openspec/board/README.md
    verify:
      - bin/verify-project .
    review_after: null
    supersedes: []
