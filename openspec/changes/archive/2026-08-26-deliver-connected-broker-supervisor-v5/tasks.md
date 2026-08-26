## 1. Build Clean Broker Controller

- [x] 1.1 Capture focused RED before the authorized module exists.
- [x] 1.2 Implement public `supervise`, broker readiness-before-launch and
  bounded closed protocol.
- [x] 1.3 Implement exact descendant identity, pidfd signaling, bounded target
  cleanup and outer broker-group cleanup.
- [x] 1.4 Enforce finite timeout, message, stream, output, identity and cleanup
  bounds with terminal fail-closed results.

## 2. Prove Connected R8/R9 Paths

- [x] 2.1 Add canonical public-`supervise` fatal/timeout cleanup and no-survivor
  scenarios without direct `_stop_group` calls.
- [x] 2.2 Add unique cleanup-removal source mutation and prove the identical
  public scenario turns red.
- [x] 2.3 Add canonical post-identity pidfd signal observation with no PID-only
  signaling.
- [x] 2.4 Add unique pidfd-to-`os.kill` source mutation and prove the identical
  public scenario turns red after signaling is reached.
- [x] 2.5 Cover protocol/order/EOF/output/timeout/cleanup bounds and dormancy.

## 3. Verify, Sync and Archive

- [x] 3.1 Retain bounded focused canonical/counterfactual evidence bound to the
  final payload.
- [x] 3.2 Run py_compile/inventory, pinned Ruff, schema smoke, strict OpenSpec,
  classification, current public scan, JSON/TOML and whitespace checks.
- [x] 3.3 Prove exact authorization, no dependency, production LOC `<=499`,
  manifest scope and dormant wiring.
- [x] 3.4 Sync the complete delta, archive the same-slug change, keep the card
  `3.inprogress` and run ordinary/high preflight.
- [x] 3.5 Prepare exactly one fresh Sol/high review handoff; do not repair,
  retry, rescue, run history/full/live or publish without GO.
