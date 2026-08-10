approval_policy = "{{CODEX_APPROVAL_POLICY}}"
sandbox_mode = "{{CODEX_SANDBOX_MODE}}"
project_doc_fallback_filenames = ["AGENTS.md"]
project_doc_max_bytes = 32768

[features]
apps = true

[projects."{{CODEX_PROJECT_KEY}}"]
trust_level = "trusted"

[mcp_servers.filesystem]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem@2026.7.10", "{{PROJECT_CONFIG_SCOPE}}"]
startup_timeout_sec = 60
enabled = true

[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp@2.1.6"]
startup_timeout_sec = 60
enabled = true

[mcp_servers.context7.env]
DEFAULT_MINIMUM_TOKENS = "10000"
