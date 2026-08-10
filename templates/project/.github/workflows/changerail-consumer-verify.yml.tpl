name: ChangeRail consumer verification

on:
  push:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout consumer
        # actions/checkout v4
        uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5
        with:
          persist-credentials: false

      - name: Read strict ChangeRail lock
        id: lock
        shell: bash
        run: |
          python3 - <<'PY'
          import json
          import os
          import re

          with open("openspec/changerail-consumer-lock.json", encoding="utf-8") as handle:
              lock = json.load(handle)
          if lock.get("schema") != "changerail.consumer-lock.v1":
              raise SystemExit("consumer lock schema is missing or unsupported")
          if lock.get("enforcement") != "strict":
              raise SystemExit("consumer CI requires strict lock enforcement")
          metadata = lock.get("changerail", {})
          source = metadata.get("source", "")
          revision = metadata.get("revision", "")
          if not re.fullmatch(r"https://[A-Za-z0-9.-]+(?::[0-9]+)?/[A-Za-z0-9._~/-]+", source):
              raise SystemExit("consumer lock source is not a public HTTPS repository")
          if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", revision):
              raise SystemExit("consumer lock revision is not exact")
          with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
              output.write(f"source={source}\n")
              output.write(f"revision={revision}\n")
          PY

      - name: Install exact ChangeRail revision
        id: changerail
        shell: bash
        env:
          CHANGERAIL_SOURCE: ${{ steps.lock.outputs.source }}
          CHANGERAIL_REVISION: ${{ steps.lock.outputs.revision }}
        run: |
          install_root="$RUNNER_TEMP/changerail-source"
          rm -rf "$install_root"
          git init "$install_root"
          git -C "$install_root" remote add origin "$CHANGERAIL_SOURCE"
          if ! git -C "$install_root" fetch --depth=1 origin "$CHANGERAIL_REVISION"; then
            echo "exact ChangeRail revision is unavailable" >&2
            exit 1
          fi
          git -C "$install_root" checkout --detach FETCH_HEAD
          test "$(git -C "$install_root" rev-parse HEAD)" = "$CHANGERAIL_REVISION"
          echo "root=$install_root" >> "$GITHUB_OUTPUT"

      - name: Install ChangeRail runtime dependencies
        run: python3 -m pip install --disable-pip-version-check -r "${{ steps.changerail.outputs.root }}/requirements-runtime.txt"

      - name: Repair lock-owned wiring
        shell: bash
        run: |
          "${{ steps.changerail.outputs.root }}/bin/bootstrap-project" "$GITHUB_WORKSPACE" \
            --changerail-root "${{ steps.changerail.outputs.root }}" \
            --refresh-wiring --skip-verify

      - name: Verify consumer
        shell: bash
        run: |
          "${{ steps.changerail.outputs.root }}/bin/verify-project" "$GITHUB_WORKSPACE" \
            --changerail-root "${{ steps.changerail.outputs.root }}"
          "$GITHUB_WORKSPACE/bin/openspec" validate --all --strict
          git -C "$GITHUB_WORKSPACE" diff --check
