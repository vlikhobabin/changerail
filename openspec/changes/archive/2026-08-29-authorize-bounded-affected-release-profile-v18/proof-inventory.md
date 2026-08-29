# Affected release profile v18 proof inventory

This docs-only artifact is the independently authored authorization-time anchor
for future v18. It is not executable input, a wire message, a receipt or a
source of review/publication authority.

Canonical section order is `semantic_rows`, `physical_rows`,
`non_task_targets`. Every fenced line is compact UTF-8 JSON with the exact key
order shown. For each section, canonical bytes append `frame(section_tag)`,
`frame(decimal_row_count)` and `frame(exact_jsonl_row)` for every row, where
`frame(x)` is eight lowercase hexadecimal digits for `len(x.encode("utf-8"))`,
one ASCII colon and the UTF-8 bytes. No Markdown bytes or digest line enter the
preimage.

- semantic row count: `35`
- physical row count: `30`
- non-task target row count: `48`
- semantic newline-list SHA-256:
  `7147ee3c4b067486162f3dc1fee218c87eb40cbdb0d7730a9a78442da7986513`
- canonical full SHA-256:
  `6587ad0b9887e79f731cdf1ef25f7ff139140747ac9f4def3aeda762c1c4ae72`

Command tokens are byte-exact authorization-HEAD argv except one explicitly
typed public-safe canonicalization. For
`drift.generated-fixture commands[2].argv[3]`, authorization HEAD MUST contain
the exact AST expression `str(DRIFT_PROJECT)`, `DRIFT_PROJECT` MUST be assigned
as `ROOT / ".runtime" / "changerail" / "ci-drift" / "example-project"`, and
`ROOT` MUST equal the real Git top level derived by
`Path(__file__).resolve().parents[1]`. The independent parser MUST first prove
that resolved absolute operand equals that exact child of `ROOT`, then encode
only `.runtime/changerail/ci-drift/example-project` in the canonical row. No
other absolute-to-relative, separator, case, symlink, traversal or environment
normalization is permitted. Thus the source expression, root derivation,
resolved value and canonical repository-relative token are one command
identity without publishing a checkout-specific absolute path.

## semantic_rows

```jsonl
{"logical_id":"openspec.validation","owner":"openspec.validation"}
{"logical_id":"config.json-parse","owner":"config.json-parse"}
{"logical_id":"config.toml-parse","owner":"config.toml-parse"}
{"logical_id":"contracts.schema-validation","owner":"contracts.schema-validation"}
{"logical_id":"python.syntax-inventory","owner":"python.syntax-inventory"}
{"logical_id":"python.runtime-selection","owner":"python.runtime-selection"}
{"logical_id":"windows.entrypoints","owner":"windows.local-matrix"}
{"logical_id":"project.bootstrap","owner":"windows.local-matrix"}
{"logical_id":"project.verify-drift","owner":"windows.local-matrix"}
{"logical_id":"windows.wiring-git-safety","owner":"windows.local-matrix"}
{"logical_id":"windows.lab-dry-run","owner":"windows.local-matrix"}
{"logical_id":"windows.runtime-wiring-dry-run","owner":"windows.local-matrix"}
{"logical_id":"python.lint","owner":"python.lint"}
{"logical_id":"ci.workflow-contract","owner":"ci.workflow-contract"}
{"logical_id":"public-surface.self-test","owner":"public-surface.self-test"}
{"logical_id":"public-surface.current","owner":"public-surface.current"}
{"logical_id":"public-surface.history","owner":"public-surface.history"}
{"logical_id":"wiring.discovery","owner":"wiring.discovery"}
{"logical_id":"runtime.diagnostics","owner":"runtime.diagnostics"}
{"logical_id":"consumer-ci","owner":"consumer-ci"}
{"logical_id":"review.verdict-validation","owner":"review.verdict-validation"}
{"logical_id":"review.fingerprint","owner":"review.fingerprint"}
{"logical_id":"review.fingerprint-benchmark","owner":"review.fingerprint-benchmark"}
{"logical_id":"review.fingerprint-cache","owner":"review.fingerprint-cache"}
{"logical_id":"review.preflight","owner":"review.preflight"}
{"logical_id":"evidence.retained","owner":"evidence.retained"}
{"logical_id":"maintenance.runner","owner":"maintenance.runner"}
{"logical_id":"delivery.manifest","owner":"delivery.manifest"}
{"logical_id":"delivery.manifest-derive","owner":"delivery.manifest-derive"}
{"logical_id":"delivery.runner","owner":"delivery.runner"}
{"logical_id":"delivery.metrics","owner":"delivery.metrics"}
{"logical_id":"openspec.archive-diagnostics","owner":"openspec.archive-diagnostics"}
{"logical_id":"drift.generated-fixture","owner":"drift.generated-fixture"}
{"logical_id":"git.whitespace","owner":"git.whitespace"}
{"logical_id":"git.ignored-status","owner":"git.ignored-status"}
```

## physical_rows

All rows have origin
`scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38`.

```jsonl
{"task_id":"openspec.validation","command_kind":"direct","commands":[["./bin/openspec","validate","--all","--strict"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"./bin/openspec","location":"commands[0].argv[0]","grammar":"exact-repository-executable"}],"owned_logical_ids":["openspec.validation"]}
{"task_id":"config.json-parse","command_kind":"direct","commands":[["python3","-m","json.tool",".mcp.json"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"module","value":"json.tool","location":"commands[0].argv[2]","grammar":"exact-python-module"},{"kind":"file","value":".mcp.json","location":"commands[0].argv[3]","grammar":"exact-repository-file"}],"owned_logical_ids":["config.json-parse"]}
{"task_id":"config.toml-parse","command_kind":"direct","commands":[["python3","-c","import tomllib; tomllib.load(open('.codex/config.toml', 'rb')); print('TOML_OK')"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"embedded-command","value":"import tomllib; tomllib.load(open('.codex/config.toml', 'rb')); print('TOML_OK')","location":"commands[0].argv[2]","grammar":"exact-python-c"},{"kind":"file","value":".codex/config.toml","location":"commands[0].argv[2]/python.open[0]","grammar":"single-quoted-repository-file"}],"owned_logical_ids":["config.toml-parse"]}
{"task_id":"contracts.schema-validation","command_kind":"direct","commands":[["python3","scripts/smoke-contract-schemas.py"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/smoke-contract-schemas.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["contracts.schema-validation"]}
{"task_id":"python.syntax-inventory","command_kind":"direct","commands":[["python3","scripts/compile-python-inventory.py"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/compile-python-inventory.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["python.syntax-inventory"]}
{"task_id":"python.runtime-selection","command_kind":"direct","commands":[["python3","scripts/smoke-python-runtime.py"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/smoke-python-runtime.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["python.runtime-selection"]}
{"task_id":"windows.local-matrix","command_kind":"direct","commands":[["python3","scripts/smoke-windows-matrix.py"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/smoke-windows-matrix.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["windows.entrypoints","project.bootstrap","project.verify-drift","windows.wiring-git-safety","windows.lab-dry-run","windows.runtime-wiring-dry-run"]}
{"task_id":"python.lint","command_kind":"direct","commands":[["ruff","check","bin","scripts"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"ruff","location":"commands[0].argv[0]","grammar":"effective-python-bin-executable"},{"kind":"directory","value":"bin","location":"commands[0].argv[2]","grammar":"exact-repository-directory"},{"kind":"directory","value":"scripts","location":"commands[0].argv[3]","grammar":"exact-repository-directory"}],"owned_logical_ids":["python.lint"]}
{"task_id":"ci.workflow-contract","command_kind":"direct","commands":[["python3","scripts/smoke-release-ci.py"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/smoke-release-ci.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["ci.workflow-contract"]}
{"task_id":"public-surface.self-test","command_kind":"direct","commands":[["python3","scripts/public-surface-scan.py","--self-test"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/public-surface-scan.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["public-surface.self-test"]}
{"task_id":"public-surface.current","command_kind":"direct","commands":[["python3","scripts/public-surface-scan.py"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/public-surface-scan.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["public-surface.current"]}
{"task_id":"public-surface.history","command_kind":"direct","commands":[["python3","scripts/public-surface-scan.py","--history"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/public-surface-scan.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["public-surface.history"]}
{"task_id":"wiring.discovery","command_kind":"direct","commands":[["python3","scripts/smoke-wiring-discovery.py"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/smoke-wiring-discovery.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["wiring.discovery"]}
{"task_id":"runtime.diagnostics","command_kind":"direct","commands":[["python3","scripts/smoke-runtime-diagnostics.py"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/smoke-runtime-diagnostics.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["runtime.diagnostics"]}
{"task_id":"consumer-ci","command_kind":"direct","commands":[["python3","scripts/smoke-consumer-ci.py"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/smoke-consumer-ci.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["consumer-ci"]}
{"task_id":"review.verdict-validation","command_kind":"direct","commands":[["python3","scripts/smoke-review-verdict-validation.py"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/smoke-review-verdict-validation.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["review.verdict-validation"]}
{"task_id":"review.fingerprint","command_kind":"direct","commands":[["python3","scripts/smoke-review-fingerprint.py"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/smoke-review-fingerprint.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["review.fingerprint"]}
{"task_id":"review.fingerprint-benchmark","command_kind":"direct","commands":[["python3","scripts/smoke-review-fingerprint-benchmark.py"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/smoke-review-fingerprint-benchmark.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["review.fingerprint-benchmark"]}
{"task_id":"review.fingerprint-cache","command_kind":"direct","commands":[["python3","scripts/smoke-review-fingerprint-cache.py"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/smoke-review-fingerprint-cache.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["review.fingerprint-cache"]}
{"task_id":"review.preflight","command_kind":"direct","commands":[["python3","scripts/smoke-review-preflight.py"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/smoke-review-preflight.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["review.preflight"]}
{"task_id":"evidence.retained","command_kind":"direct","commands":[["python3","scripts/smoke-retained-evidence.py"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/smoke-retained-evidence.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["evidence.retained"]}
{"task_id":"maintenance.runner","command_kind":"direct","commands":[["python3","scripts/smoke-maintenance-runner.py"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/smoke-maintenance-runner.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["maintenance.runner"]}
{"task_id":"delivery.manifest","command_kind":"direct","commands":[["python3","scripts/smoke-delivery-manifest.py"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/smoke-delivery-manifest.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["delivery.manifest"]}
{"task_id":"delivery.manifest-derive","command_kind":"direct","commands":[["python3","scripts/smoke-delivery-manifest-derive.py"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/smoke-delivery-manifest-derive.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["delivery.manifest-derive"]}
{"task_id":"delivery.runner","command_kind":"direct","commands":[["python3","scripts/smoke-delivery-runner.py"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/smoke-delivery-runner.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["delivery.runner"]}
{"task_id":"delivery.metrics","command_kind":"direct","commands":[["python3","scripts/smoke-delivery-metrics.py"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/smoke-delivery-metrics.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["delivery.metrics"]}
{"task_id":"openspec.archive-diagnostics","command_kind":"direct","commands":[["python3","scripts/smoke-openspec-archive-diagnostics.py"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"python3","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/smoke-openspec-archive-diagnostics.py","location":"commands[0].argv[1]","grammar":"exact-repository-script"}],"owned_logical_ids":["openspec.archive-diagnostics"]}
{"task_id":"drift.generated-fixture","command_kind":"sequential-group","commands":[["rm","-rf",".runtime/changerail/ci-drift"],["./bin/bootstrap-project",".runtime/changerail/ci-drift/example-project","--name","example-project","--kind","generic","--lock-enforcement","none"],["python3","scripts/smoke-drift.py","--project",".runtime/changerail/ci-drift/example-project"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"rm","location":"commands[0].argv[0]","grammar":"effective-path-executable"},{"kind":"directory","value":".runtime/changerail/ci-drift","location":"commands[0].argv[2]","grammar":"exact-repository-runtime-directory"},{"kind":"executable","value":"./bin/bootstrap-project","location":"commands[1].argv[0]","grammar":"exact-repository-executable"},{"kind":"directory","value":".runtime/changerail/ci-drift/example-project","location":"commands[1].argv[1]","grammar":"exact-repository-runtime-directory"},{"kind":"executable","value":"python3","location":"commands[2].argv[0]","grammar":"effective-path-executable"},{"kind":"script","value":"scripts/smoke-drift.py","location":"commands[2].argv[1]","grammar":"exact-repository-script"},{"kind":"directory","value":".runtime/changerail/ci-drift/example-project","location":"commands[2].argv[3]","grammar":"authorization-head-str(DRIFT_PROJECT)-exact-root-child-to-repository-relative"}],"owned_logical_ids":["drift.generated-fixture"]}
{"task_id":"git.whitespace","command_kind":"direct","commands":[["git","diff","--check"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"git","location":"commands[0].argv[0]","grammar":"effective-path-executable"}],"owned_logical_ids":["git.whitespace"]}
{"task_id":"git.ignored-status","command_kind":"direct","commands":[["git","status","--short","--ignored"]],"origin":"scripts/run-release-baseline.py@fe2f50398e535c3d265ef7664b2b1a2102505e38","operands":[{"kind":"executable","value":"git","location":"commands[0].argv[0]","grammar":"effective-path-executable"}],"owned_logical_ids":["git.ignored-status"]}
```

## non_task_targets

```jsonl
{"target_id":"repository.root","kind":"directory","value":".","origin":"authorization-head","grammar":"exact-real-git-toplevel-no-symlink"}
{"target_id":"requirements.runtime","kind":"file","value":"requirements-runtime.txt","origin":"authorization-head","grammar":"exact-repository-file"}
{"target_id":"requirements.dev","kind":"file","value":"requirements-dev.txt","origin":"authorization-head","grammar":"exact-repository-file"}
{"target_id":"python.effective","kind":"executable","value":"python3","origin":"effective-path","grammar":"real-non-symlink-python-version>=3.11"}
{"target_id":"distribution.jsonschema","kind":"module","value":"jsonschema==4.23.0","origin":"requirements-runtime.txt","grammar":"exact-distribution-version-and-root"}
{"target_id":"distribution.markdown-it-py","kind":"module","value":"markdown-it-py==3.0.0","origin":"requirements-runtime.txt","grammar":"exact-distribution-version-and-root"}
{"target_id":"distribution.PyYAML","kind":"module","value":"PyYAML==6.0.3","origin":"requirements-runtime.txt","grammar":"exact-distribution-version-and-root"}
{"target_id":"distribution.ruff","kind":"module","value":"ruff==0.6.9","origin":"requirements-dev.txt","grammar":"exact-distribution-version-and-root"}
{"target_id":"package-root.purelib","kind":"directory","value":"sysconfig.get_paths()[purelib]","origin":"python.effective","grammar":"exact-real-non-symlink-package-root"}
{"target_id":"package-root.platlib","kind":"directory","value":"sysconfig.get_paths()[platlib]","origin":"python.effective","grammar":"exact-real-non-symlink-package-root"}
{"target_id":"executable.ruff","kind":"executable","value":"ruff","origin":"python.effective-bin","grammar":"real-non-symlink-exact-version-0.6.9"}
{"target_id":"executable.git","kind":"executable","value":"git","origin":"effective-path","grammar":"usable-git-with-exact-repository-root"}
{"target_id":"executable.node","kind":"executable","value":"node","origin":"effective-path","grammar":"bounded-usable-version-probe"}
{"target_id":"executable.npm","kind":"executable","value":"npm","origin":"effective-path","grammar":"bounded-usable-version-probe"}
{"target_id":"executable.npx","kind":"executable","value":"npx","origin":"effective-path","grammar":"bounded-usable-version-probe"}
{"target_id":"executable.openspec","kind":"executable","value":"./bin/openspec","origin":"authorization-head","grammar":"real-repository-executable-offline-version-1.3.1"}
{"target_id":"environment.OPENSPEC_VERSION","kind":"embedded-command","value":"unset-or-1.3.1","origin":"process-environment","grammar":"no-conflicting-value"}
{"target_id":"runtime.root","kind":"directory","value":".runtime/changerail/affected-release-v18","origin":"authorization-inventory","grammar":"exact-missing-or-real-direct-child-under-.runtime/changerail"}
{"target_id":"task-root.openspec.validation","kind":"directory","value":".runtime/changerail/affected-release-v18/openspec.validation","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.config.json-parse","kind":"directory","value":".runtime/changerail/affected-release-v18/config.json-parse","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.config.toml-parse","kind":"directory","value":".runtime/changerail/affected-release-v18/config.toml-parse","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.contracts.schema-validation","kind":"directory","value":".runtime/changerail/affected-release-v18/contracts.schema-validation","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.python.syntax-inventory","kind":"directory","value":".runtime/changerail/affected-release-v18/python.syntax-inventory","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.python.runtime-selection","kind":"directory","value":".runtime/changerail/affected-release-v18/python.runtime-selection","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.windows.local-matrix","kind":"directory","value":".runtime/changerail/affected-release-v18/windows.local-matrix","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.python.lint","kind":"directory","value":".runtime/changerail/affected-release-v18/python.lint","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.ci.workflow-contract","kind":"directory","value":".runtime/changerail/affected-release-v18/ci.workflow-contract","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.public-surface.self-test","kind":"directory","value":".runtime/changerail/affected-release-v18/public-surface.self-test","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.public-surface.current","kind":"directory","value":".runtime/changerail/affected-release-v18/public-surface.current","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.public-surface.history","kind":"directory","value":".runtime/changerail/affected-release-v18/public-surface.history","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.wiring.discovery","kind":"directory","value":".runtime/changerail/affected-release-v18/wiring.discovery","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.runtime.diagnostics","kind":"directory","value":".runtime/changerail/affected-release-v18/runtime.diagnostics","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.consumer-ci","kind":"directory","value":".runtime/changerail/affected-release-v18/consumer-ci","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.review.verdict-validation","kind":"directory","value":".runtime/changerail/affected-release-v18/review.verdict-validation","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.review.fingerprint","kind":"directory","value":".runtime/changerail/affected-release-v18/review.fingerprint","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.review.fingerprint-benchmark","kind":"directory","value":".runtime/changerail/affected-release-v18/review.fingerprint-benchmark","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.review.fingerprint-cache","kind":"directory","value":".runtime/changerail/affected-release-v18/review.fingerprint-cache","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.review.preflight","kind":"directory","value":".runtime/changerail/affected-release-v18/review.preflight","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.evidence.retained","kind":"directory","value":".runtime/changerail/affected-release-v18/evidence.retained","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.maintenance.runner","kind":"directory","value":".runtime/changerail/affected-release-v18/maintenance.runner","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.delivery.manifest","kind":"directory","value":".runtime/changerail/affected-release-v18/delivery.manifest","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.delivery.manifest-derive","kind":"directory","value":".runtime/changerail/affected-release-v18/delivery.manifest-derive","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.delivery.runner","kind":"directory","value":".runtime/changerail/affected-release-v18/delivery.runner","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.delivery.metrics","kind":"directory","value":".runtime/changerail/affected-release-v18/delivery.metrics","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.openspec.archive-diagnostics","kind":"directory","value":".runtime/changerail/affected-release-v18/openspec.archive-diagnostics","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.drift.generated-fixture","kind":"directory","value":".runtime/changerail/affected-release-v18/drift.generated-fixture","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.git.whitespace","kind":"directory","value":".runtime/changerail/affected-release-v18/git.whitespace","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
{"target_id":"task-root.git.ignored-status","kind":"directory","value":".runtime/changerail/affected-release-v18/git.ignored-status","origin":"physical-task-id","grammar":"exact-absent-direct-child"}
```

## Static migration

Authorization-HEAD `scripts/run-release-baseline.py` has 36 `Step(...)` calls.
The only removed physical processes are the four standalone calls owned by the
local Windows matrix: entrypoints, wiring Git safety, bootstrap and
verify-project. The only grouped calls are generated-drift reset, bootstrap and
assertion. The assertion's checkout-dependent `str(DRIFT_PROJECT)` argv is
proved from its exact authorization-HEAD AST/root assignment and serialized by
the single public-safe canonicalization declared above; this changes neither
the command target nor migration cardinality. Therefore
`36 - 4 - (3 - 1) = 30`; the matrix row owns six semantic leaves and every
other physical row owns one, so all 35 semantic rows remain.
