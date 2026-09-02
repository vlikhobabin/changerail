#!/usr/bin/env python3
# ruff: noqa: E701, E702
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import sys

import yaml


class CoreLoader(yaml.SafeLoader):
    pass


CoreLoader.yaml_implicit_resolvers = copy.deepcopy(yaml.SafeLoader.yaml_implicit_resolvers)
for key, rules in CoreLoader.yaml_implicit_resolvers.items():
    CoreLoader.yaml_implicit_resolvers[key] = [rule for rule in rules
                                               if rule[0] != "tag:yaml.org,2002:bool"]

DEPENDENCIES = """python3 -m venv .runtime/changerail/ci-venv
.runtime/changerail/ci-venv/bin/python -m pip install --disable-pip-version-check -r requirements-dev.txt
echo "$PWD/.runtime/changerail/ci-venv/bin" >> "$GITHUB_PATH"
./bin/openspec --version >/dev/null
"""
EXPECTED = {"name":"ChangeRail CI","on":{"push":None,"pull_request":None,"workflow_dispatch":None},
            "permissions":{"contents":"read"},"jobs":{"verify":{"name":"Verify ChangeRail release gates",
            "runs-on":"ubuntu-latest","steps":[
            {"name":"Check out repository","uses":"actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5","with":{"fetch-depth":"0"}},
            {"name":"Set up Node.js for OpenSpec wrapper","uses":"actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020","with":{"node-version":"20"}},
            {"name":"Prepare offline release dependencies","run":DEPENDENCIES},
            {"name":"Run canonical full release","run":"python3 scripts/run-release-baseline.py --profile full-release"}]}}}


def validate_workflow(path: Path) -> None:
    parsed = yaml.load(path.read_text(encoding="utf-8"), Loader=CoreLoader)
    if parsed != EXPECTED:
        raise ValueError("canonical four-step CI object mismatch")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--workflow",type=Path,default=Path(__file__).resolve().parents[1]/".github/workflows/changerail-ci.yml"); parser.add_argument("--json",action="store_true")
    args = parser.parse_args(argv)
    try: validate_workflow(args.workflow); report = {"schema":"changerail.release-ci-smoke.v1","summary":{"status":"pass","total":1,"passed":1,"failed":0}}
    except Exception as exc: report = {"schema":"changerail.release-ci-smoke.v1","summary":{"status":"fail","total":1,"passed":0,"failed":1},"error":str(exc)}
    print(json.dumps(report,sort_keys=True) if args.json else f"summary: {report['summary']['status']} ({report['summary']['passed']}/1 passed, {report['summary']['failed']} failed)")
    return 0 if report["summary"]["status"] == "pass" else 1


if __name__ == "__main__": raise SystemExit(main(sys.argv[1:]))
