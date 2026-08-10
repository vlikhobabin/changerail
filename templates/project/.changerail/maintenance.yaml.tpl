schema: changerail.maintenance-policy.v1
catalog_path: .changerail/knowledge.yaml
generated_index_path: .changerail/KNOWLEDGE.md
scan:
  include_globs:
    - .changerail/KNOWLEDGE.md
    - AGENTS.md
    - docs/**/*.md
    - openspec/**/*.md
    - .changerail/**/*.yaml
  exclude_globs:
    - .runtime/**
    - internal/**
  active_scope_globs:
    - AGENTS.md
    - docs/**/*.md
    - openspec/**/*.md
  enabled_detectors:
    - catalog-coverage
    - repository-orphans
    - markdown-local-links
    - generated-freshness
  fail_on: major
  timeout_seconds: 900
