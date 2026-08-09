## Context

Maintenance contracts are opt-in: repositories without
`.changerail/maintenance.yaml` remain valid and existing delivery/review/publish
behavior is unaffected. This change wires maintenance into generated consumers
only when the operator asks for it, while keeping the broader verification
profile redesign in card `050` out of scope.

Bootstrap already owns consumer project templates, helper wiring, native
Windows generated-copy metadata and verifier-readable policy. Maintenance
wiring should extend those mechanisms instead of creating a separate
installation model.

## Goals / Non-Goals

**Goals:**
- Add explicit `--with-maintenance` bootstrap opt-in.
- Generate maintenance policy/catalog/helper/ignore wiring only for opted-in
  consumers.
- Teach `verify-project` to detect maintenance opt-in from tracked
  maintenance declarations.
- Verify helper, schema, config and ignore wiring for opted-in consumers.
- Keep non-opted-in consumers unchanged and valid.
- Cover POSIX symlink wiring and native Windows generated-copy refresh for
  maintenance helpers.

**Non-Goals:**
- Do not make maintenance part of default bootstrap.
- Do not implement the broader profile policy redesign owned by card `050`.
- Do not run a full maintenance scan as part of bootstrap verification.
- Do not silently add write permissions, scheduler config or credentials.

## Decisions

1. The opt-in flag is `--with-maintenance`. Alternative: infer opt-in from
   project kind. Rejected because maintenance is orthogonal to `--kind` and
   existing consumers must remain unchanged.
2. Verifier opt-in is based on tracked maintenance declarations, not ignored
   runtime state. A consumer with `.changerail/maintenance.yaml`, maintenance
   helper wiring or generated ownership metadata must have the complete
   maintenance wiring set. Alternative: only check when the flag was used.
   Rejected because verification must work after the bootstrap command is gone.
3. Bootstrap verification checks reachability and wiring only; it does not run
   full maintenance scan. Alternative: run scan during bootstrap. Rejected
   because scan coverage and detector quality are repository-content dependent
   and broader detector completeness belongs to `060-05`.
4. Native Windows generated-copy ownership extends the existing generated
   wiring manifest. Alternative: use symlinks for maintenance helpers on
   Windows. Rejected to preserve the current no-privilege Windows backend.
5. Existing POSIX wiring keeps symlink behavior and helper discovery contracts.

## Risks / Trade-offs

- [Risk] Partial opt-in artifacts can leave consumers in a confusing state. ->
  Mitigation: verifier treats any tracked maintenance declaration as opt-in and
  fails closed until the complete wiring set is present.
- [Risk] Default consumers may accidentally inherit maintenance policy. ->
  Mitigation: templates render maintenance files only behind
  `--with-maintenance`; absent artifacts remain valid.
- [Risk] Windows generated copies can drift. -> Mitigation: generated ownership
  metadata and refresh checks include maintenance helper paths.

## Migration Plan

Add opt-in bootstrap rendering and verifier checks. Existing consumers do
nothing. Consumers that want maintenance run bootstrap/adoption refresh with
`--with-maintenance`, commit the tracked policy/helper wiring, and keep runtime
reports under ignored `.runtime/changerail/maintenance/`.

Rollback removes the opt-in flag and verifier checks while leaving existing
generic consumer bootstrap behavior unchanged.

## Open Questions

- none
