# Design: public surface scanner

The scanner will be a small Python script that walks explicit files/directories
or a default set of tracked public roots. It will skip ignored runtime/local
directories such as `.git`, `.runtime`, `internal`, `__pycache__` and
`node_modules`.

Initial checks focus on `/opt/*` path leaks:

- allow `/opt/changerail`;
- allow `/opt/example-project`, `/opt/example-a`, `/opt/example-b`;
- allow `/opt/opsx` only on lines that look like documented historical,
  migration, legacy or pre-rename references.

The script exits non-zero with file/line diagnostics when it finds a disallowed
path. Additional private-name or secret patterns can be added later without
changing call sites.
