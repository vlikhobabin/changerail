import json

print(
    json.dumps(
        {
            "schema": "changerail.maintenance-detector-result.v1",
            "id": "adapter-valid",
            "status": "fail",
            "findings": [
                {
                    "id": "valid-adapter:architecture-rule",
                    "severity": "major",
                    "code": "adapter_fixture_finding",
                    "message": "valid adapter finding fixture",
                    "path": "docs/index.md",
                }
            ],
            "errors": [],
        },
        sort_keys=True,
    )
)
