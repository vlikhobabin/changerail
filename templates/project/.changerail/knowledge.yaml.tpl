schema: changerail.repository-knowledge.v1
records:
  - path: .changerail/KNOWLEDGE.md
    status: generated
    type: generated
    owner: "{{PROJECT_NAME}}"
    source_globs:
      - .changerail/knowledge.yaml
      - .changerail/maintenance.yaml
    verify:
      - bin/changerail-maintenance render-index --check
    review_after: null
    supersedes: []
  - path: .changerail/knowledge.yaml
    status: active
    type: reference
    owner: "{{PROJECT_NAME}}"
    source_globs:
      - .changerail/knowledge.yaml
    verify:
      - bin/changerail-maintenance validate-catalog
      - bin/changerail-maintenance render-index --check
    review_after: null
    supersedes: []
  - path: .changerail/maintenance.yaml
    status: active
    type: reference
    owner: "{{PROJECT_NAME}}"
    source_globs:
      - .changerail/maintenance.yaml
    verify:
      - bin/changerail-maintenance validate-catalog
      - bin/changerail-maintenance scan --json
    review_after: null
    supersedes: []
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
  - path: openspec/board/card-template.md
    status: active
    type: reference
    owner: "{{PROJECT_NAME}}"
    source_globs:
      - openspec/board/card-template.md
    verify:
      - bin/verify-project .
      - bin/changerail-maintenance validate-catalog
      - bin/changerail-maintenance render-index --check
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
