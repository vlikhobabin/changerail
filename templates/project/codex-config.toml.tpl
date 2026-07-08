approval_policy = "never"
sandbox_mode = "danger-full-access"
project_doc_fallback_filenames = ["AGENTS.md"]

[features]
apps = true

[projects."{{PROJECT_PATH}}"]
trust_level = "trusted"

[mcp_servers.filesystem]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "{{PROJECT_PATH}}"]
startup_timeout_sec = 60
enabled = true

[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp@2.1.6"]
startup_timeout_sec = 60
enabled = true

[mcp_servers.context7.env]
DEFAULT_MINIMUM_TOKENS = "10000"
