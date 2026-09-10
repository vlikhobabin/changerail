# Local upstream OpenSpec dependency

This project dependency pins **unmodified OpenSpec 1.3.1** through the manifest
and npm lockfile. `bin/openspec` uses this installation for canonical validation
and the explicit native ChangeRail route. Existing frozen runs cannot adopt a
different installation or process silently.

From the repository root:

```sh
./tools/openspec/bootstrap.sh --offline
./bin/openspec --version
```

Node.js >=20.19.0 and npm must already exist. Bootstrap explicitly installs the
locked dependency tree from the existing npm cache, ignores lifecycle scripts,
and disables audit/funding/update notifications. `npm ci` replaces only this
installation's `node_modules`; it does not install global dependencies. Missing
cached tarballs fail the operation. Obtaining dependencies on another machine is
a separate provisioning action, not an automatic fallback or part of delivery.

The wrapper preserves the caller's working directory so an adapter can operate
on an explicit disposable project. It invokes only the installed
`tools/openspec/node_modules/@fission-ai/openspec/bin/openspec.js`, checks the package
name/version and entrypoint containment, and fails on a missing or mismatched
installation. It never calls `npx`, downloads a package, searches a global
OpenSpec executable or falls back to a developer's npm cache. The lockfile, not
an editable global install, defines the dependency set; reinstall to restore it.
The runtime check is not an integrity audit of every installed dependency file.

`OPENSPEC_TELEMETRY=0`, `DO_NOT_TRACK=1` and `CI=true` disable upstream 1.3.1
telemetry. Completion auto-configuration is disabled and install scripts are
skipped. The wrapper does not automatically update OpenSpec or generate agent
instructions; explicit native commands still have their documented effects.
Environment flags and offline npm installation **are not full network
isolation**: Node, the OS and the model-provider delivery sessions remain
separate trust/network boundaries. Registry URLs in the lockfile are package
provenance, not instructions to contact the registry at runtime.

Wrapper tests remain in the ChangeRail source repository and are not installed
in consuming projects. Run `node --test tools/openspec/test-wrapper.mjs` only
from the ChangeRail source root when maintaining the wrapper. Development source
attachments may expose the same tests through links; runtime archives omit them.

Upgrade the exact manifest pin, regenerate the lockfile in an explicitly
authorized provisioning step, update the compatibility check, and rerun the
adapter contract suite before adopting a newer upstream version. Do not fork
upstream schemas just to change board status handling.

## Initial isolated verification (2026-09-06)

The lockfile was generated using `npm install --package-lock-only --offline
--ignore-scripts --no-audit --no-fund`; no registry download was needed. Explicit
offline bootstrap then installed 74 packages from the existing cache, and the
real local CLI returned `1.3.1`. All eight Node contract tests passed: missing
dependency, wrong version, external package symlink, cwd/argument/env forwarding,
real version, lock integrity fields, empty-cache failure, and explicit bootstrap
choice. Shell syntax checks and the launcher JavaScript syntax check passed.

The empty-cache test concretely received npm's offline cache-miss failure. These
checks do not constitute packet capture, a full installation integrity audit,
an agent review, or autonomous card-delivery evidence. Temporary test fixture
directories are removed by test teardown; staged installed dependencies remain
available for the Python adapter's native-CLI contract tests.
