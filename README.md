# ThingsPanel MCP

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/thingspanel-mcp.svg)](https://pypi.org/project/thingspanel-mcp/)
[![PyPI version](https://badge.fury.io/py/thingspanel-mcp.svg)](https://pypi.org/project/thingspanel-mcp/)

ThingsPanel MCP connects MCP-compatible assistants to ThingsPanel and ThingsVis APIs. It offers both focused IoT tools and individually named API tools with fixed, source-audited routes.

[English](https://github.com/ThingsPanel/thingspanel-mcp/blob/codex/release-0.1.10/README.md) | [中文](https://github.com/ThingsPanel/thingspanel-mcp/blob/codex/release-0.1.10/README_CN.md)

## What it includes

- 376 MCP tools: 363 generated API tools plus 13 focused device, telemetry, dashboard, and control tools.
- The generated set covers 311 ThingsPanel and 52 ThingsVis API operations, including device, telemetry, alarms, groups, products, service access, dashboards, and uploads.
- 177 generated read operations. The remaining 186 write or control operations require the tool argument confirmed=true.
- Structured JSON results, business-code error detection, path encoding, file upload support, and bounded SSE/WebSocket reads.
- Authentication profiles for ThingsPanel and ThingsVis. Authorization is always enforced by the connected service.

The complete allow-listed API inventory is in src/thingspanel_mcp/api_manifest.json. The tool definitions fix the HTTP method and route; callers provide path_params, query, body, and optional file_path values.

## Requirements and installation

- Python 3.8 or later.
- A ThingsPanel account and a credential accepted by the target API. ThingsVis operations may require ThingsVis credentials as well.

Install from PyPI:

    python -m pip install --upgrade thingspanel-mcp

Run without a persistent installation using uv:

    uvx --from thingspanel-mcp thingspanel-mcp --help

Install from source:

    git clone https://github.com/ThingsPanel/thingspanel-mcp.git
    cd thingspanel-mcp
    python -m pip install .

## Authentication and permissions

ThingsPanel Community supports SYS_ADMIN and TENANT_ADMIN. It does not have tenant subusers; tenant-user accounts are an Enterprise edition capability. ThingsPanel API keys map to tenant-administrator permissions. A system administrator must use a ThingsPanel login JWT.

ThingsVis credentials are separate from ThingsPanel credentials. The ThingsVis SSO exchange uses the ThingsPanel JWT from the selected profile; ThingsVis validates that token server-to-server and derives the role from the verified identity. The MCP caller cannot submit a role or user identity to elevate access.

Use a profile for each identity. The default profile is used when a tool does not specify profile. The 13 focused convenience tools use the default profile; the generated API tools accept an explicit profile argument.

Create ~/.thingspanel/config.json:

    {
      "base_url": "https://thingspanel.example.com",
      "api_prefix": "/api/v1",
      "thingsvis_base_url": "https://thingsvis.example.com",
      "thingsvis_api_prefix": "/api/v1",
      "profiles": {
        "default": {
          "thingspanel_token": "<tenant-admin-jwt>",
          "thingsvis_token": "<thingsvis-jwt>",
          "thingsvis_open_api_key": "<dashboard-open-api-key>"
        },
        "tenant_admin": {
          "thingspanel_token": "<tenant-admin-jwt>"
        },
        "superadmin": {
          "thingspanel_token": "<sys-admin-jwt>"
        }
      }
    }

Keep this file private; on macOS or Linux, restrict access with chmod 600 ~/.thingspanel/config.json. Never commit real credentials.

Environment variables can override the default profile and endpoints:

    THINGSPANEL_CONFIG_PATH
    THINGSPANEL_BASE_URL
    THINGSPANEL_API_PREFIX
    THINGSPANEL_TOKEN
    THINGSPANEL_API_KEY
    THINGSPANEL_REFRESH_TOKEN
    THINGSVIS_BASE_URL
    THINGSVIS_API_PREFIX
    THINGSVIS_TOKEN
    THINGSVIS_REFRESH_TOKEN
    THINGSVIS_OPEN_API_KEY
    THINGSVIS_INTERNAL_SECRET

Named profile credentials use THINGSPANEL_PROFILE_<NAME>_TOKEN, THINGSPANEL_PROFILE_<NAME>_API_KEY, THINGSPANEL_PROFILE_<NAME>_THINGSPANEL_REFRESH_TOKEN, THINGSPANEL_PROFILE_<NAME>_THINGSVIS_TOKEN, and THINGSPANEL_PROFILE_<NAME>_THINGSVIS_REFRESH_TOKEN. For example, THINGSPANEL_PROFILE_SUPERADMIN_TOKEN. Environment credentials are loaded at process startup.

For a single default identity, the command line is also available:

    thingspanel-mcp --token "<ThingsPanel login JWT>" --base-url "https://thingspanel.example.com"

Use --api-key only when connecting as a tenant administrator. The token and API-key command-line arguments may be visible to local process inspection; a protected config file or a secret manager is preferable.

## Configure an MCP client

The default transport is stdio. SSE is available with --transport sse. Keep credentials outside client configuration by pointing the server to a protected config file or by using the client's environment support.

### Codex

Add this to ~/.codex/config.toml:

    [mcp_servers.thingspanel]
    command = "uvx"
    args = ["--from", "thingspanel-mcp==0.1.10", "thingspanel-mcp"]

    [mcp_servers.thingspanel.env]
    THINGSPANEL_CONFIG_PATH = "/absolute/path/to/.thingspanel/config.json"

Restart or refresh Codex MCP servers after changing the configuration.

### Claude Desktop

Add a server entry to claude_desktop_config.json:

    {
      "mcpServers": {
        "thingspanel": {
          "command": "uvx",
          "args": ["--from", "thingspanel-mcp==0.1.10", "thingspanel-mcp"],
          "env": {
            "THINGSPANEL_CONFIG_PATH": "/absolute/path/to/.thingspanel/config.json"
          }
        }
      }
    }

### WorkBuddy

For local stdio use, add a server entry to ~/.workbuddy/mcp.json:

    {
      "mcpServers": {
        "thingspanel": {
          "type": "stdio",
          "command": "uvx",
          "args": ["--from", "thingspanel-mcp==0.1.10", "thingspanel-mcp"],
          "env": {
            "THINGSPANEL_CONFIG_PATH": "/absolute/path/to/.thingspanel/config.json"
          }
        }
      }
    }

This local configuration is separate from publishing a WorkBuddy marketplace connector. Marketplace submission also needs connector metadata, an MCP manifest, an icon, and review. For user-entered credentials, follow WorkBuddy's token-auth configuration. A Skill is optional for standard MCP tool schemas, but is useful for guiding tool selection and safe workflows across this large tool set. See the [WorkBuddy connector guide](https://open.workbuddy.cn/docs/connector).

## Calling tools

Each generated tool represents exactly one allow-listed API operation. For example, a device-detail tool uses path_params for its route identifier:

    path_params = {"id": "device-id"}
    profile = "tenant_admin"

Supply query parameters in query and JSON request data in body. File-upload tools accept file_path and, where needed, upload_field. Choose the profile that owns the requested data; do not ask the MCP server to impersonate another role.

For every generated write or control tool, first explain the intended action and obtain the user's approval in the host application. Then call the tool with confirmed=true. If confirmed is false, the tool returns confirmation_required and a request preview without sending the request. This flag is an additional guard, not a replacement for user approval or backend authorization.

Streaming tools accept stream_messages from 1 to 20 and stream_seconds from 1 to 30. Defaults are 5 messages and 5 seconds.

## Results and troubleshooting

Successful calls return a structured result similar to:

    {"ok": true, "status": 200, "data": {...}}

Failed calls return ok=false with status and error information where available. ThingsPanel business codes are checked even when HTTP status is 200.

- A configuration error naming a profile means that profile is missing or lacks credentials for that service.
- A 401 or 403 means the credential is invalid or its service-side role cannot access that operation.
- A response with confirmation_required is a write preview. Set confirmed=true only after the action has been approved.
- A missing_path_parameter error means a required route value is absent from path_params.
- SSE and WebSocket results are intentionally bounded; a partial result may mean the configured time or message limit was reached.
- For URL or proxy issues, check the service base URL and API prefix for that environment.

## Security notes

- The server never trusts a caller-supplied role; the connected backend is authoritative.
- API tools are allow-listed from the checked-in manifest. They do not accept arbitrary method or URL values.
- 186 generated writes and controls require confirmed=true, and remain subject to backend permissions.
- Tokens and API keys are not printed by request error handling. Keep local config files private and rotate credentials according to your organization's policy.

## Development

Run the unit tests with python -m pytest. Build release files with python -m build, then validate their metadata with python -m twine check dist/*. Use tools/build_api_manifest.py to regenerate the checked-in API inventory and tools/audit_apifox_source.py to review source-documentation differences.

## License

Apache License 2.0. See LICENSE.
