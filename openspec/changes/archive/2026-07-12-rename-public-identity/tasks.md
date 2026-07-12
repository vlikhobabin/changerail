## 1. Public Identity Rename

- [x] 1.1 Update README, root repository instructions and durable docs to use `ChangeRail`, `changerail` and `/opt/changerail`.
- [x] 1.2 Update `AGENTS.md`, `AGENTS.shared.md`, board docs and active OpenSpec specs to describe ChangeRail as the workflow/toolchain and OpenSpec as the artifact dependency.
- [x] 1.3 Add migration notes that OPSX was the previous name and document GitHub repository rename plus local `origin` update.

## 2. Verification

- [x] 2.1 Run `./bin/openspec validate rename-public-identity --strict`.
- [x] 2.2 Run `./bin/openspec validate --all --strict`.
- [x] 2.3 Run `git diff --check`.
- [x] 2.4 Run a public-surface scan proving tracked docs do not contain real local consumer project names or paths.
- [x] 2.5 Review remaining `OPSX`, `opsx`, `/opt/opsx` and GitHub `opsx` matches in active surface and classify each as migration/history or fix it.
