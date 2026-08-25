## 1. Decision sources and forensic boundary

- [x] 1.1 Confirm exact published base `b027d30441ad366931aa5c89203a4286efbfa4b1` and published rescue predecessor are remote-reachable.
- [x] 1.2 Record private prototype commits and runtime evidence as forensic-only, with no cherry-pick, merge, tracked evidence reuse or publication claim.
- [x] 1.3 Prove the decision payload adds zero executable/test/runtime LOC.

## 2. Bounded ownership and authorization

- [x] 2.1 Bind exact H authorization `350/false` and implementation `<=349` to structural history only.
- [x] 2.2 Bind exact I authorization `500/true` and implementation `<=499` to isolated execution only.
- [x] 2.3 Bind exact R authorization `500/true` and implementation `<=499` to registry/affected selection only.
- [x] 2.4 Bind exact A authorization `500/true` and implementation `<=499` to bounded execution, receipt and CI authority only.
- [x] 2.5 Prove H and I scopes are disjoint and may run concurrently, while R depends on both and A depends on R.

## 3. Proof and performance boundary

- [x] 3.1 Specify pre-child admission and per-step timeout/output/process cleanup for both profiles.
- [x] 3.2 Specify deterministic per-step telemetry and bounded diagnostics without timing authority.
- [x] 3.3 Specify atomic payload-bound receipt plus exact manifest/review/pub/CI equality and affected non-authority.
- [x] 3.4 Specify measured bottleneck optimization after A publication and native Windows certification before final capture.
- [x] 3.5 Reserve Sol/`high` for normal successor reviews and the single Sol/`xhigh` audit for final unchanged certification.

## 4. Documentation verification

- [x] 4.1 Validate the target change and `changerail-release-ci` capability with strict OpenSpec.
- [x] 4.2 Validate all OpenSpec changes/specs, JSON, TOML, exact authorization objects and reciprocal order assertions.
- [x] 4.3 Run current-only public-surface, source-classification, whitespace and scoped preflight checks.
- [x] 4.4 Do not run history scan, full baseline, live Windows, successor implementation, review, commit or push during FF.
