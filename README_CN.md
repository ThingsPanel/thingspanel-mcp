# ThingsPanel MCP：Encore 迁移开发版

此分支是 `0.2.0.dev0` 开发候选，尚未发布。它从源码核对的 Encore API 注册 MCP 工具；旧版 0.1.11 的 378 个旧接口工具不再默认注册。迁移状态、未完成项和测试结果见 [任务清单](ENCORE_MIGRATION_TASKS.md)。

## 安装与配置

```bash
python3 -m pip install -e .
export THINGSPANEL_ENCORE_BASE_URL=https://your-thingspanel-entry
export THINGSPANEL_TOKEN='<登录令牌>'
thingspanel-mcp --transport stdio
```

MCP STDIO 的 stdout 用于协议消息，请使用宿主安全注入凭据，不要把令牌写进仓库。Encore 必须显式配置服务地址；HTTPS 为默认要求，仅本机回环允许 HTTP。`--base-url` 指定 Encore 地址，`--token` 可用但不建议在命令行历史暴露令牌。命名 profile 沿用本项目的配置方式，租户由令牌和服务端授权确定。

服务默认注册 Community 主线 `7f694779` 的已核对工具。设备、接入模板和分组的原生 `/api/v2` 依赖候选 `d4e0540b` 或兼容版本完成部署，确认后才能设置 `THINGSPANEL_ENABLE_NATIVE_METADATA=1`。开关只启用对应工具，不能部署后端，也不会向旧 API 回退。

Northbound 数据转发工具同样默认关闭；只有确认服务已构建并部署后才设置 `THINGSPANEL_ENABLE_NORTHBOUND=1`。单独打开开关不会让服务自动进入发行镜像。

调用写入工具须提供 `confirmed=true`；按工具说明提供请求体、`idempotency_key`、`if_match`。先读取最新 ETag，再按原样传回。写入未收到响应时结果未知，先查询实际状态；仅对接口保证幂等的请求用原键重试。凭据和调试信息可能敏感，不记录到日志。

`confirmed` 是工具调用参数，不能单独证明人已审阅或批准；实际用户确认由 MCP 宿主负责。敏感响应会返回给授权调用方，宿主也应避免记录和缓存。

运行 `python3 -m pytest -q` 检查本地测试。当前测试状态和真实服务联调限制以任务清单为准。实际部署、旧客户端迁移及每个工具的最终生产验收尚需单独完成。
