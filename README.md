# ChangeRail pre-consolidation archive

This synthetic commit preserves the Git history that was reachable from every branch in the repository snapshot taken on 2026-09-02.

- manifest.json is the authoritative ref-to-object map for all 108 branch refs and 5 release tags in the snapshot.
- Every unique branch-tip commit is a direct parent of this commit; duplicate branch-tip object IDs are represented once as parents.
- The tag archive/pre-consolidation-20260902 is the durable archive entry point.
- This archive records history only; it does not designate a development or release branch.
