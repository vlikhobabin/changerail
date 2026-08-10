# changerail-python-runtime Specification

## Purpose
Зафиксировать supported Python runtime, shared interpreter selection,
override, ignored runtime state и actionable diagnostics для tracked ChangeRail
Python helpers.

## Requirements
### Requirement: Supported Python runtime
ChangeRail MUST declare a supported Python runtime for tracked Python helpers
and MUST separate runtime dependencies from release-only tooling.

#### Scenario: Maintainer reads compatibility notes
- **WHEN** a maintainer reads ChangeRail compatibility documentation
- **THEN** the documentation declares Python 3.11 or newer as the minimum
  supported runtime for Python helpers
- **AND** it identifies `tomllib` as a stdlib runtime module requirement
- **AND** it identifies `jsonschema` as a runtime package requirement for
  schema-backed contract helpers
- **AND** it identifies `markdown-it-py` / import module `markdown_it` as a
  runtime package requirement for maintenance Markdown link checks

#### Scenario: Runtime dependencies are explicit
- **WHEN** the repository dependency files are inspected
- **THEN** runtime packages needed by public Python helpers are listed in
  `requirements-runtime.txt`
- **AND** release-only tooling remains distinguishable from the runtime package
  set

### Requirement: Shared Python runtime selection
ChangeRail MUST provide one shared runtime selector for tracked Python helper
entrypoints before helper-specific Python imports execute.

#### Scenario: Helper starts with supported runtime
- **WHEN** a ChangeRail Python helper entrypoint runs on a host with a supported
  interpreter and required runtime modules
- **THEN** the shared selector starts the helper with that interpreter
- **AND** helper-specific behavior executes normally

#### Scenario: Host runtime is too old
- **WHEN** the shared selector probes an interpreter older than Python 3.11
- **THEN** the helper exits non-zero before helper-specific imports run
- **AND** the diagnostic names the required Python version and remediation
  path

#### Scenario: Required runtime module is missing
- **WHEN** the shared selector probes a Python 3.11 or newer interpreter that
  lacks a required runtime module
- **THEN** the helper exits non-zero before helper-specific imports run
- **AND** the diagnostic names the missing module and the runtime dependency
  install path

### Requirement: Explicit Python override
ChangeRail Python helper entrypoints MUST support an explicit interpreter
override without editing tracked shebangs.

#### Scenario: Operator selects interpreter
- **WHEN** an operator sets `CHANGERAIL_PYTHON` to a supported interpreter and
  runs a ChangeRail Python helper entrypoint
- **THEN** the shared selector uses that interpreter for the helper invocation

#### Scenario: Override is invalid
- **WHEN** `CHANGERAIL_PYTHON` points to a missing, non-executable or
  unsupported interpreter
- **THEN** the helper exits non-zero before helper-specific imports run
- **AND** the diagnostic identifies the override as invalid and explains how to
  remove or correct it

### Requirement: Runtime bootstrap state is ignored
ChangeRail runtime bootstrap MUST write interpreter/environment check state
only under ignored ChangeRail runtime paths.

#### Scenario: Selector records runtime state
- **WHEN** the shared selector records interpreter check state
- **THEN** the record is written under `.runtime/changerail/python-runtime/`
- **AND** no tracked file is created or modified by the runtime bootstrap
