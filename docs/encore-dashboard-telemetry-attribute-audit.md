# 看板、遥测和属性接口核对（2026-11-01）

源码基线：Community main `7f694779`；设备元数据候选 `d4e0540b`。候选是否已部署必须由实际服务确认。下述已实现指 MCP 源码，不代表真实运行环境验收。

| 场景 | Encore 能力及 MCP 状态 | 限制 |
|---|---|---|
| 设备统计看板 | 候选 `GET /api/v2/device-statistics`，由 `encore_device_statistics` 提供 | 设备总数等按权限范围统计；候选的在线、离线和告警观测尚未接入，保留 null/unknown，不得当作零 |
| 在线趋势、消息数量、看板 CRUD | 核对的主线与候选中未发现对应 Encore 用户接口 | 旧 MCP 汇总和趋势依赖旧 API；ThingsVis 看板是独立服务，不能假装是 Encore 接口。待后端提供并确认契约 |
| 当前遥测 / 属性 | 候选 `GET /api/v2/devices/:deviceID/readings`，`encore_list_device_readings` 对这两类默认发 `latestOnly=true` | 后端仍通过 Community 运行时读取；需要候选及其运行时；客户端不回退旧 API |
| 遥测历史 / 聚合 | 同一候选接口，提供 `identifier`、`from_time`、`to_time`，可选 `aggregation` 和 `window` | 时间、范围与聚合窗口限制由后端校验；真实运行时待验收 |
| 属性写入 | 未发现核对范围内可用的 Encore 原生属性写入契约 | 不将设备命令冒充属性写入；等待后端契约及权限、设备回执语义 |

Kernel 的 `/v1/telemetry/current`、`history` 和 `control-logs` 在该源码版本通过 `legacy.NewFromEnv()` 调旧后端，并非上表候选的原生用户契约。本次不默认暴露或绕过租户授权，避免把兼容层当成已迁移能力。
