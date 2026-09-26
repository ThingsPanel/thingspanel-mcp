# ThingsPanel MCP

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/thingspanel-mcp.svg)](https://pypi.org/project/thingspanel-mcp/)
[![PyPI version](https://badge.fury.io/py/thingspanel-mcp.svg)](https://pypi.org/project/thingspanel-mcp/)

ThingsPanel MCP 将 MCP 兼容的 AI 助手连接到 ThingsPanel 和 ThingsVis API。它同时提供面向物联网场景的快捷工具，以及绑定固定、经过源码审计的 API 路由工具。

[English](https://github.com/ThingsPanel/thingspanel-mcp/blob/codex/release-0.1.10/README.md) | [中文](https://github.com/ThingsPanel/thingspanel-mcp/blob/codex/release-0.1.10/README_CN.md)

## 功能范围

- 共注册 376 个 MCP 工具：363 个自动生成的 API 工具，以及 13 个设备、遥测、看板和控制快捷工具。
- 生成的 API 工具覆盖 311 个 ThingsPanel 与 52 个 ThingsVis 操作，包括设备、遥测、告警、分组、产品、服务接入、看板和文件上传。
- 生成工具中有 177 个读取操作；其余 186 个写入或控制操作要求传入 confirmed=true。
- 返回结构化 JSON，检查业务错误码，安全编码路径参数，支持文件上传，并限制 SSE/WebSocket 的读取时长和消息数量。
- 支持 ThingsPanel 与 ThingsVis 认证 profile；实际权限始终由连接的服务端校验。

完整的 API allow-list 位于 src/thingspanel_mcp/api_manifest.json。每个生成工具绑定固定的 HTTP 方法和路由；调用方只传 path_params、query、body 以及可选的 file_path。

## 环境要求与安装

- Python 3.8 或更高版本。
- ThingsPanel 账户及目标 API 接受的凭证；调用 ThingsVis 操作时可能还需要 ThingsVis 凭证。

从 PyPI 安装：

    python -m pip install --upgrade thingspanel-mcp

使用 uv 临时运行，不做全局安装：

    uvx --from thingspanel-mcp thingspanel-mcp --help

从源码安装：

    git clone https://github.com/ThingsPanel/thingspanel-mcp.git
    cd thingspanel-mcp
    python -m pip install .

## 身份验证与权限

ThingsPanel 社区版支持 SYS_ADMIN 和 TENANT_ADMIN，不包含租户下的子用户；租户用户属于企业版能力。ThingsPanel API Key 在平台中映射为租户管理员权限。超管必须使用 ThingsPanel 登录 JWT。

ThingsVis 凭证与 ThingsPanel 凭证分开配置。ThingsVis SSO 使用所选 profile 中的 ThingsPanel JWT；ThingsVis 服务端会验证该 JWT，并从验证后的身份派生角色。MCP 调用方不能在参数中提交角色或其他用户身份来提升权限。

为每个身份配置 profile。未显式传入 profile 时使用 default。13 个快捷工具固定使用 default profile；363 个生成 API 工具支持显式传入 profile。

创建 ~/.thingspanel/config.json：

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

请保护该文件；macOS/Linux 可使用 chmod 600 ~/.thingspanel/config.json 限制访问。不要把真实凭证提交到代码仓库。

以下环境变量可覆盖 default profile 或服务地址：

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

命名 profile 凭证可使用 THINGSPANEL_PROFILE_<名称>_TOKEN、THINGSPANEL_PROFILE_<名称>_API_KEY、THINGSPANEL_PROFILE_<名称>_THINGSPANEL_REFRESH_TOKEN、THINGSPANEL_PROFILE_<名称>_THINGSVIS_TOKEN 和 THINGSPANEL_PROFILE_<名称>_THINGSVIS_REFRESH_TOKEN。例如：THINGSPANEL_PROFILE_SUPERADMIN_TOKEN。环境变量在 MCP 进程启动时读取。

单一 default 身份也可通过命令行设置：

    thingspanel-mcp --token "<ThingsPanel登录JWT>" --base-url "https://thingspanel.example.com"

只有在以租户管理员身份连接时才使用 --api-key。命令行参数可能被本机进程检查工具读取；更推荐使用受保护的配置文件或密钥管理工具。

## MCP 客户端配置

默认传输方式是 stdio，也可通过 --transport sse 启动 SSE。请不要把真实凭证写进客户端配置；通过受保护配置文件或客户端环境变量提供认证信息。

### Codex

将以下内容加入 ~/.codex/config.toml：

    [mcp_servers.thingspanel]
    command = "uvx"
    args = ["--from", "thingspanel-mcp==0.1.10", "thingspanel-mcp"]

    [mcp_servers.thingspanel.env]
    THINGSPANEL_CONFIG_PATH = "/绝对路径/.thingspanel/config.json"

修改配置后，重启或刷新 Codex MCP 服务器。

### Claude Desktop

在 claude_desktop_config.json 中添加 MCP server：

    {
      "mcpServers": {
        "thingspanel": {
          "command": "uvx",
          "args": ["--from", "thingspanel-mcp==0.1.10", "thingspanel-mcp"],
          "env": {
            "THINGSPANEL_CONFIG_PATH": "/绝对路径/.thingspanel/config.json"
          }
        }
      }
    }

### WorkBuddy

使用本机 stdio 模式时，在 ~/.workbuddy/mcp.json 中添加：

    {
      "mcpServers": {
        "thingspanel": {
          "type": "stdio",
          "command": "uvx",
          "args": ["--from", "thingspanel-mcp==0.1.10", "thingspanel-mcp"],
          "env": {
            "THINGSPANEL_CONFIG_PATH": "/绝对路径/.thingspanel/config.json"
          }
        }
      }
    }

本机 MCP 配置与 WorkBuddy 连接器市场发布是两个流程。市场连接器还需要连接器元信息、MCP 清单、图标并通过审核；用户自填凭证时需按 WorkBuddy 的 token 认证配置添加表单。标准 MCP 工具描述不强制要求 Skill；但工具较多时，Skill 可帮助模型选择工具并遵守安全流程。详情见 [WorkBuddy 连接器规范](https://open.workbuddy.cn/docs/connector)。

## 如何调用工具

每个生成工具只对应一个 allow-list 中的 API 操作。例如调用设备详情工具时，路径变量放入 path_params：

    path_params = {"id": "device-id"}
    profile = "tenant_admin"

查询参数放入 query，JSON 请求体放入 body。文件上传工具可传入 file_path；需要时通过 upload_field 指定上传字段。选择拥有目标数据权限的 profile，不要要求 MCP 冒用其他角色。

每个生成的写入或控制工具都必须先向用户说明具体动作，并在宿主应用中获得确认，再传入 confirmed=true。confirmed=false 时，工具返回 confirmation_required 和请求预览，不会发送请求。该参数只是额外保护，不能代替用户确认或后端授权。

流式工具支持 stream_messages 1–20 条、stream_seconds 1–30 秒；默认最多读取 5 条消息或 5 秒。

## 返回结果与常见问题

成功响应示例：

    {"ok": true, "status": 200, "data": {...}}

失败响应会返回 ok=false，并在可用时包含 HTTP 状态码及错误信息。即使 HTTP 状态码为 200，ThingsPanel MCP 也会检查响应中的业务码。

- 配置错误中提示某 profile 时，说明该 profile 不存在，或缺少调用对应服务所需的凭证。
- 401/403 表示凭证无效，或服务端角色无权调用该操作。
- 返回 confirmation_required 表示这是写操作预览；只有在用户确认后才设置 confirmed=true。
- missing_path_parameter 表示 path_params 缺少路由所需参数。
- SSE/WebSocket 结果有意限制了消息数量和时长；部分结果可能是达到上限后的返回。
- 遇到 URL 或代理错误时，检查对应环境的服务地址与 API 前缀。

## 安全说明

- 服务端是最终权限依据；MCP 不信任调用方自报的角色。
- API 工具由仓库内的 manifest allow-list 生成，不接受调用方任意指定 HTTP 方法或 URL。
- 186 个生成写入/控制工具要求 confirmed=true，且仍受后端权限控制。
- 请求失败日志不会打印完整凭证。请保护本机配置文件，并按组织凭证策略定期轮换密钥。

## 开发与发布

运行单元测试：python -m pytest。构建发行包：python -m build；上传前检查元数据：python -m twine check dist/*。使用 tools/build_api_manifest.py 重新生成 API 清单，使用 tools/audit_apifox_source.py 检查源码与 API 文档差异。

## 许可证

Apache License 2.0，详见 LICENSE。
