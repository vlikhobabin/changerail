import json

print(
    json.dumps(
        {
            "schema": "changerail.maintenance-detector-result.v1",
            "id": "adapter-unsafe-path",
            "status": "fail",
            "findings": [
                {
                    "id": "unsafe-path:absolute",
                    "severity": "major",
                    "code": "adapter_unsafe_fixture",
                    "message": "unsafe path fixture",
                    "path": "/tmp/outside.md",
                }
            ],
            "errors": [],
        },
        sort_keys=True,
    )
)
