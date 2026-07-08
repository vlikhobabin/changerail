## ADDED Requirements

### Requirement: Общая методология агентов
OPSX MUST provide tracked file `AGENTS.shared.md`, который задает reusable
agent methodology для OPSX consumers.

#### Scenario: Проект-потребитель получает OPSX methodology
- **WHEN** consumer project bootstrapped from OPSX templates
- **THEN** project receives methodology content derived from
  `AGENTS.shared.md`

### Requirement: Generic public-safe content
Shared methodology MUST avoid private workspace names, customer data, secrets,
local traces, credentials и machine-specific runtime state.

#### Scenario: Ревью публичного репозитория
- **WHEN** `AGENTS.shared.md` reviewed before commit
- **THEN** file contains only generic OPSX rules and documented example paths
  such as `/opt/opsx` and `/opt/example-project`

### Requirement: Покрытие workflow
Shared methodology MUST cover OPSX lifecycle from exploration through publish,
including board usage, OpenSpec artifacts, review gates, verification evidence и
scoped publishing.

#### Scenario: Агент читает shared methodology
- **WHEN** agent receives shared methodology in consumer project
- **THEN** agent has enough workflow guidance to follow `explore -> ff -> do ->
  review -> pub` without relying on project-private OPSX notes

### Requirement: Drift-aware embedding
Shared methodology MUST state that generated consumer-project sections are
subject to future drift checks against OPSX source of truth.

#### Scenario: Future verify-project проверяет generated instructions
- **WHEN** consumer project has embedded OPSX methodology section
- **THEN** `verify-project` can treat that section as generated content that
  must match `AGENTS.shared.md`
