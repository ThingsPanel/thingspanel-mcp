# ThingsPanel MCP 全局任务清单

> 目标：为 ThingsPanel 超级管理员、租户管理员/用户及 ThingsVis 建立完整 MCP API 能力；每个工具逐项实现并测试。
> 工作仓库：`/Users/junhong/Downloads/code/thingspanel-mcp`。ThingsPanel backend 与 ThingsVis server 作为只读参考。
> 状态：`[ ]` 未开始；`[~]` 进行中；`[x]` 当前有效路由已实现/测试，或文档孤儿接口已核实无当前 router 注册并审计排除；`[!]` 未解决阻塞，记录于 `error-log.md`。

## 全局阶段

- [x] G0 盘点工作区、服务进程、代理路径、当前源码与文档基数。
- [x] G1 建立源码优先 API 清单；315 次注册去重为 314 条 ThingsPanel 路由，另从 Apifox 1.1.6 的 328 个页面抽取 323 个唯一 method/path，核对得到 257 项重合、66 项 Apifox-only、57 项当前 router-only；并核对 Swagger 差异、重复路由和传输类型。
- [x] G2 实现按身份 profile 管理 ThingsPanel `x-token`/`x-api-key` 与 ThingsVis Bearer/internal token；不接受自报角色。
- [x] G3 依据当前 router 实现 ThingsPanel HTTP 工具；311/314 路由可调用，基础校验与写操作确认已覆盖，3 条基础设施路由不作为业务工具开放。
- [x] G4 支持有界 SSE/WebSocket、multipart 文件上传及 ThingsVis 内部令牌路由；3 条基础设施路由审计为不开放。
- [x] G5 已实现 52/52 条 ThingsVis handler；SSO 用 ThingsPanel 服务端 JWT 核验，角色从真实后端 authority 派生，忽略调用者提交的 userInfo/role；超管、租户管理员、普通用户的真实 MCP SSO 均成功，返回角色分别为 `SUPER_ADMIN`、`TENANT_ADMIN`、`EDITOR`。
- [x] G6 使用真实本地账号经 FastMCP 工具管理器验证角色：个人信息接口三类角色均成功；超管系统指标成功、租户角色拒绝；超管可跨租户列设备及读详情，租户管理员/用户只能读本租户示例设备。
- [x] G7 依据源码清单完成工具覆盖、363/363 FastMCP 精确路由契约测试、ThingsVis GET 基线与三角色 SSO，以及真实系统/设备读取权限矩阵；写工具统一要求显式确认，本轮未对共享开发数据执行写入或删除。最终报告：[final-report.md](./final-report.md)。

## 覆盖基线

> ThingsPanel backend 当前路由 AST 清点：315 次注册、314 个唯一 method/path（`POST /api/v1/device/auth` 重复注册，需核实）；Swagger 98 路径/138 操作，与当前源码 132 项吻合，182 项源码路由未在 Swagger 命中，6 项 Swagger 路由未在当前 router 命中。ThingsVis server 当前 52 个可用 handler（排除 OPTIONS 与 health 的 method-not-allowed 占位方法）。在线 Apifox llms.txt（ThingsPanel 1.1.6）含 323 个唯一接口操作，其中 257 项与 router 精确吻合、66 项无当前注册；backend AST 有 57 项未列于 Apifox。合并当前 ThingsPanel router、ThingsVis handler 与不重复计数的 Swagger/Apifox 文档孤儿项，共 436 个清单操作；文档孤儿接口已审计排除。
> 角色不是 MCP 输入参数：ThingsPanel 受保护路由由 `x-token` + Casbin 决策；`x-api-key` 会被平台映射为 TENANT_ADMIN，不能代表超管或普通租户用户。ThingsVis 另用 Bearer JWT。

## API 操作逐项跟踪

> 状态 `[x]` 对当前有效路由表示对应 MCP 工具已注册且 FastMCP 契约测试核验 exact method/path 与路径参数；对 Apifox-only 路由表示已审计无当前 router 注册并排除。它不表示对真实账号执行了每项业务操作。角色集成及越权测试单独记录于 G6。



### Apifox 1.1.6 · 当前 router 未注册（审计后排除）

> 这些 64 个唯一 method/path 只出现在在线 Apifox 导出中；对当前 backend router 的精确 AST 清单没有注册项，因此当前服务无法接收请求。已作为过时/未部署接口审计并排除，不生成无法调用的 MCP 工具。两条同时出现在 Swagger mismatch 的路径已在上一节记录，避免重复计数。

| 状态 | 方法 | 路径 | 依据 | 处理 |
|---|---|---|---|---|
| [x] | `DELETE` | `/api/v1/casbin/user/device` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `DELETE` | `/api/v1/casbin/user/device_group` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `DELETE` | `/api/v1/forwarding/rule/:id` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `DELETE` | `/api/v1/forwarding/source/:id` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `DELETE` | `/api/v1/forwarding/target/:id` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `DELETE` | `/api/v1/product/:id` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `DELETE` | `/api/v1/vis/plugin/dashboard/:id` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/casbin/user/device` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/casbin/user/device_group` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/device/batch/template` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/device/detail/:id/user` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/device/group/detail/:id/user` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/device/preRegister` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/device/preRegister/export` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/devices/:device_id/data` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/form/config` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/forwarding/rule` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/forwarding/rule/:id` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/forwarding/script/:id` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/forwarding/source` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/forwarding/source/:id` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/forwarding/target` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/forwarding/target/:id` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/health/kafka` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/open/keys/tenant` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/plugin/device/list` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/product` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/vis/plugin/dashboard` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/vis/plugin/list` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/vis/plugin/local` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v1/vis/plugin/share/:id` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `GET` | `/api/v2/form/config` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `POST` | `/api/v1/algorithms/results` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `POST` | `/api/v1/casbin/user/device` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `POST` | `/api/v1/casbin/user/device_group` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `POST` | `/api/v1/device/batch/import` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `POST` | `/api/v1/device/disconnect` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `POST` | `/api/v1/device/model/custom/commands/` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `POST` | `/api/v1/device/preRegister` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `POST` | `/api/v1/forwarding/rule` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `POST` | `/api/v1/forwarding/script` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `POST` | `/api/v1/forwarding/script/test` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `POST` | `/api/v1/forwarding/source` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `POST` | `/api/v1/forwarding/target` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `POST` | `/api/v1/login/wechat` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `POST` | `/api/v1/notice/test` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `POST` | `/api/v1/notification/services/config/sms/test` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `POST` | `/api/v1/plugin/notification` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `POST` | `/api/v1/product` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `POST` | `/api/v1/vis/plugin/dashboard` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `POST` | `/api/v1/vis/plugin/share` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `POST` | `/api/v1/vis/plugin/up` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `POST` | `/broadcast` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `PUT` | `/api/v1/casbin/user/device` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `PUT` | `/api/v1/casbin/user/device_group` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `PUT` | `/api/v1/device/model/custom/commands/` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `PUT` | `/api/v1/forwarding/rule` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `PUT` | `/api/v1/forwarding/rule/status` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `PUT` | `/api/v1/forwarding/script` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `PUT` | `/api/v1/forwarding/source` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `PUT` | `/api/v1/forwarding/target` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `PUT` | `/api/v1/product` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `PUT` | `/api/v1/sys_function/:function_id` | Apifox llms export only | 当前 router 无注册；审计排除 |
| [x] | `PUT` | `/api/v1/vis/plugin/dashboard` | Apifox llms export only | 当前 router 无注册；审计排除 |

### Apifox/Swagger · source mismatch

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [ ] | `PUT` | `/api/v1/ota/package/` | 规范中有、当前 router 未匹配；核实是否弃用/改名 | 待源码/运行时核实 |
| [ ] | `GET` | `/api/v1/protocol_plugin` | 规范中有、当前 router 未匹配；核实是否弃用/改名 | 待源码/运行时核实 |
| [ ] | `POST` | `/api/v1/protocol_plugin` | 规范中有、当前 router 未匹配；核实是否弃用/改名 | 待源码/运行时核实 |
| [ ] | `PUT` | `/api/v1/protocol_plugin` | 规范中有、当前 router 未匹配；核实是否弃用/改名 | 待源码/运行时核实 |
| [ ] | `DELETE` | `/api/v1/protocol_plugin/:id` | 规范中有、当前 router 未匹配；核实是否弃用/改名 | 待源码/运行时核实 |
| [ ] | `GET` | `/api/v1/protocol_plugin/device_config_form` | 规范中有、当前 router 未匹配；核实是否弃用/改名 | 待源码/运行时核实 |

### ThingsPanel · alarm

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/alarm/config` | 源码：alarm.go:33 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/alarm/config` | 源码：alarm.go:24 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/alarm/config` | 源码：alarm.go:30 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/alarm/config/:id` | 源码：alarm.go:27 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/alarm/device/counts` | 获取租户下告警状态的设备数量 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/alarm/info` | 源码：alarm.go:47 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/alarm/info` | 源码：alarm.go:41 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/alarm/info/batch` | 源码：alarm.go:44 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/alarm/info/config/device` | 源码：alarm.go:55 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/alarm/info/history` | 源码：alarm.go:49 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/alarm/info/history` | 源码：alarm.go:51 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/alarm/info/history/:id` | 源码：alarm.go:60 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/alarm/info/history/:id` | 源码：alarm.go:57 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/alarm/info/history/device` | 源码：alarm.go:53 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · attribute

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `DELETE` | `/api/v1/attribute/datas/:id` | 源码：attribute_data.go:21 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/attribute/datas/:id` | 源码：attribute_data.go:15 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/attribute/datas/get` | 源码：attribute_data.go:27 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/attribute/datas/key` | 源码：attribute_data.go:30 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/attribute/datas/pub` | 源码：attribute_data.go:24 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/attribute/datas/set/logs` | 源码：attribute_data.go:18 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · board

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/board` | 源码：board.go:25 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/board` | 源码：board.go:16 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/board` | 源码：board.go:22 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/board/:id` | 源码：board.go:19 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/board/:id` | 源码：board.go:28 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/board/device` | 源码：board.go:50 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/board/device/total` | 源码：board.go:48 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/board/home` | 源码：board.go:31 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/board/tenant` | 源码：board.go:56 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/board/tenant/device/info` | 源码：board.go:60 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/board/tenant/user/info` | 源码：board.go:58 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/board/trend` | 源码：board.go:34 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/board/user/info` | 源码：board.go:66 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/board/user/update` | 源码：board.go:68 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/board/user/update/password` | 源码：board.go:70 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · casbin

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/casbin/function` | 源码：casbin.go:18 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/casbin/function` | 源码：casbin.go:15 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/casbin/function` | 源码：casbin.go:17 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/casbin/function/:id` | 源码：casbin.go:16 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/casbin/user` | 源码：casbin.go:24 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/casbin/user` | 源码：casbin.go:21 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/casbin/user` | 源码：casbin.go:23 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/casbin/user/:id` | 源码：casbin.go:22 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · command

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/command/datas/:id` | 源码：command_data.go:21 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/command/datas/pub` | 源码：command_data.go:18 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/command/datas/set/logs` | 源码：command_data.go:15 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · dashboard-menu

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `DELETE` | `/api/v1/dashboard-menu/:dashboardId` | 源码：dashboard_menu.go:16 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/dashboard-menu/:dashboardId` | 源码：dashboard_menu.go:14 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/dashboard-menu/:dashboardId` | 源码：dashboard_menu.go:15 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · data_script

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/data_script` | 源码：data_script.go:25 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/data_script` | 源码：data_script.go:16 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/data_script` | 源码：data_script.go:22 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/data_script/:id` | 源码：data_script.go:19 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/data_script/enable` | 源码：data_script.go:31 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/data_script/quiz` | 源码：data_script.go:28 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · datapolicy

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/datapolicy` | 源码：datapolicy.go:19 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/datapolicy` | 源码：datapolicy.go:16 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · device

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/device` | 源码：device.go:30 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device` | 源码：device.go:16 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/device` | 源码：device.go:22 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/:device_id/debug` | 源码：device.go:78 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/:device_id/debug/logs` | 源码：device.go:80 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/:device_id/debug/status` | 源码：device.go:79 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/device/:id` | 源码：device.go:19 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/device/active` | 源码：device.go:25 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/auth` | 设备动态认证 | 公开/专用凭证（逐项核实） |
| [x] | `GET` | `/api/v1/device/check/:deviceNumber` | 源码：device.go:33 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/connect/form` | 源码：device.go:45 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/connect/info` | 源码：device.go:48 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/dashboard-templates` | 源码：device.go:188 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/dashboard-templates/:id/compatible-devices` | 源码：device.go:189 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/dashboard-templates/:id/instances` | 源码：device.go:190 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/detail/:id` | 源码：device.go:28 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/gateway-register` | 源码：router_init.go:118 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/gateway-sub-register` | 源码：router_init.go:120 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/group` | 源码：device.go:206 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/group` | 源码：device.go:197 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/device/group` | 源码：device.go:203 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/device/group/:id` | 源码：device.go:200 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/group/counts` | 源码：device.go:212 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/group/detail/:id` | 源码：device.go:215 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/device/group/relation` | 源码：device.go:224 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/group/relation` | 源码：device.go:228 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/group/relation` | 源码：device.go:222 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/group/relation/list` | 源码：device.go:226 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/group/tree` | 源码：device.go:209 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/list` | 源码：device.go:39 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/map/telemetry/:id` | 源码：device.go:69 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/market/bundles` | 源码：device.go:167 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/market/bundles/:bundleKey` | 源码：device.go:168 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/market/bundles/:bundleKey/precheck` | 源码：device.go:169 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/market/bundles/download` | 源码：device.go:171 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/market/bundles/install` | 源码：device.go:173 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/market/bundles/install/:id` | 源码：device.go:175 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/device/market/bundles/install/:id/bindings` | 源码：device.go:177 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/market/bundles/install/:id/compensate` | 源码：device.go:181 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/market/bundles/install/:id/retry` | 源码：device.go:179 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/market/bundles/installations` | 源码：device.go:183 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/market/bundles/publish-draft` | 源码：device.go:165 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/market/dashboard-bundles` | 源码：device.go:163 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/market/dashboard-bundles/analyze` | 源码：device.go:161 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/metrics/:id` | 源码：device.go:60 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/metrics/chart` | 源码：device.go:86 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/metrics/condition/menu` | 源码：device.go:66 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/metrics/menu` | 源码：device.go:63 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/model/attributes` | 源码：device.go:249 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/model/attributes` | 源码：device.go:246 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/device/model/attributes` | 源码：device.go:248 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/device/model/attributes/:id` | 源码：device.go:247 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/model/commands` | 源码：device.go:265 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/model/commands` | 源码：device.go:262 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/device/model/commands` | 源码：device.go:264 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/device/model/commands/:id` | 源码：device.go:263 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/model/custom/commands` | 源码：device.go:274 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/model/custom/commands` | 源码：device.go:271 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/device/model/custom/commands` | 源码：device.go:273 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/model/custom/commands/:deviceId` | 源码：device.go:275 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/device/model/custom/commands/:id` | 源码：device.go:272 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/model/custom/control` | 源码：device.go:284 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/model/custom/control` | 源码：device.go:281 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/device/model/custom/control` | 源码：device.go:283 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/device/model/custom/control/:id` | 源码：device.go:282 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/model/events` | 源码：device.go:257 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/model/events` | 源码：device.go:254 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/device/model/events` | 源码：device.go:256 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/device/model/events/:id` | 源码：device.go:255 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/model/source/at/list` | 源码：device.go:235 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/model/telemetry` | 源码：device.go:241 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/model/telemetry` | 源码：device.go:238 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/device/model/telemetry` | 源码：device.go:240 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/device/model/telemetry/:id` | 源码：device.go:239 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/online/status/:id` | 源码：device.go:75 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/online/status/ws` | 获取设备在线状态 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/online/status/ws/batch` | 源码：router_init.go:99 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/selector` | 源码：device.go:89 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/service/access/batch` | 源码：device.go:83 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/son/add` | 源码：device.go:42 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/status/history` | 源码：device.go:95 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/sub-list/:id` | 源码：device.go:54 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/device/sub-remove` | 源码：device.go:57 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/telemetry/latest` | 源码：device.go:92 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/template` | 源码：device.go:123 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/template` | 源码：device.go:111 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/device/template` | 源码：device.go:117 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/device/template/:id` | 源码：device.go:114 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/template/chart` | 源码：device.go:135 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/template/chart/select` | 源码：device.go:138 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/template/detail/:id` | 源码：device.go:120 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/template/market/detail/:market_id` | 源码：device.go:151 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/template/market/install` | 源码：device.go:153 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/template/market/list` | 源码：device.go:149 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/template/market/login` | 源码：device.go:144 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/template/market/publish` | 源码：device.go:147 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/template/market/refresh` | 源码：device.go:145 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/template/menu` | 源码：device.go:126 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/template/selector` | 源码：device.go:132 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/template/stats` | 源码：device.go:129 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/tenant/list` | 源码：device.go:36 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device/topic-mappings` | 源码：device.go:101 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/topic-mappings` | 源码：device.go:100 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/device/topic-mappings/:id` | 源码：device.go:103 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/device/topic-mappings/:id` | 源码：device.go:102 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/device/update/config` | 源码：device.go:72 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device/update/voucher` | 源码：device.go:51 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · device_config

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/device_config` | 源码：device_config.go:25 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/device_config` | 源码：device_config.go:16 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/device_config` | 源码：device_config.go:22 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/device_config/:id` | 源码：device_config.go:19 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device_config/:id` | 源码：device_config.go:31 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/device_config/batch` | 源码：device_config.go:34 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device_config/connect` | 源码：device_config.go:37 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device_config/menu` | 源码：device_config.go:28 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device_config/metrics/condition/menu` | 源码：device_config.go:46 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device_config/metrics/menu` | 源码：device_config.go:43 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/device_config/voucher_type` | 源码：device_config.go:40 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · devices

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/devices/:device_id/diagnostics` | 源码：router_init.go:126 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · dict

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/dict` | 源码：sys_dict.go:25 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/dict/column` | 源码：sys_dict.go:16 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/dict/column/:id` | 源码：sys_dict.go:31 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/dict/enum` | 源码：sys_dict.go:22 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/dict/language` | 源码：sys_dict.go:19 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/dict/language/:id` | 源码：sys_dict.go:34 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/dict/language/:id` | 源码：sys_dict.go:28 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/dict/protocol/service` | 源码：sys_dict.go:37 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · event

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/event/datas` | 源码：event_data.go:14 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · events

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/events` | 源码：sse.go:13 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · expected

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `POST` | `/api/v1/expected/data` | 源码：expected_data.go:15 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/expected/data/:id` | 源码：expected_data.go:16 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/expected/data/list` | 源码：expected_data.go:14 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · file

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `POST` | `/api/v1/file/up` | 源码：upload.go:15 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · infra

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [!] | `GET` | `/files/*filepath` | 核对是否属于 MCP 产品 API 范围 | 基础设施路由（默认不做业务工具） |
| [x] | `GET` | `/health` | 核对是否属于 MCP 产品 API 范围 | 基础设施路由（默认不做业务工具） |
| [!] | `GET` | `/metrics` | 核对是否属于 MCP 产品 API 范围 | 基础设施路由（默认不做业务工具） |
| [!] | `GET` | `/swagger/*any` | 核对是否属于 MCP 产品 API 范围 | 基础设施路由（默认不做业务工具） |

### ThingsPanel · login

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `POST` | `/api/v1/login` | 用户登录 | 公开/专用凭证（逐项核实） |

### ThingsPanel · logo

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/logo` | 源码：router_init.go:93 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/logo` | 源码：logo.go:16 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · message_push

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `POST` | `/api/v1/message_push` | 源码：message_push.go:15 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/message_push/config` | 源码：message_push.go:19 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/message_push/config` | 源码：message_push.go:21 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/message_push/logout` | 源码：message_push.go:17 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · notification

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `POST` | `/api/v1/notification/services/config` | 源码：notification_services_config.go:15 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/notification/services/config/:type` | 源码：notification_services_config.go:18 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/notification/services/config/e-mail/test` | 源码：notification_services_config.go:21 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · notification_group

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `POST` | `/api/v1/notification_group` | 源码：notification_groups.go:16 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/notification_group/:id` | 源码：notification_groups.go:19 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/notification_group/:id` | 源码：notification_groups.go:28 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/notification_group/:id` | 源码：notification_groups.go:22 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/notification_group/list` | 源码：notification_groups.go:25 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · notification_history

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/notification_history/list` | 源码：notification_history.go:17 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · open

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/open/keys` | 源码：open_api_keys.go:17 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/open/keys` | 源码：open_api_keys.go:16 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/open/keys` | 源码：open_api_keys.go:18 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/open/keys/:id` | 源码：open_api_keys.go:19 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · operation_logs

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/operation_logs` | 源码：operation_logs.go:15 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · ota

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/ota/download/files/upgradePackage/:path/:file` | 源码：router_init.go:102 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/ota/package` | 源码：ota.go:19 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/ota/package` | 源码：ota.go:16 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/ota/package` | 源码：ota.go:18 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/ota/package/:id` | 源码：ota.go:17 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/ota/task` | 源码：ota.go:28 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/ota/task` | 源码：ota.go:24 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/ota/task/:id` | 源码：ota.go:26 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/ota/task/detail` | 源码：ota.go:30 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/ota/task/detail` | 源码：ota.go:32 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · plugin

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `POST` | `/api/v1/plugin/device/config` | 源码：router_init.go:86 | 公开/专用凭证（逐项核实） |
| [x] | `POST` | `/api/v1/plugin/devices` | 源码：router_init.go:87 | 公开/专用凭证（逐项核实） |
| [x] | `POST` | `/api/v1/plugin/heartbeat` | 源码：router_init.go:85 | 公开/专用凭证（逐项核实） |
| [x] | `POST` | `/api/v1/plugin/service/access` | 源码：router_init.go:89 | 公开/专用凭证（逐项核实） |
| [x] | `POST` | `/api/v1/plugin/service/access/list` | 源码：router_init.go:88 | 公开/专用凭证（逐项核实） |

### ThingsPanel · protocol_plugin

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/protocol_plugin/config_form` | 源码：protocol_plugin.go:15 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · reset

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `POST` | `/api/v1/reset/password` | 源码：router_init.go:92 | 公开/专用凭证（逐项核实） |

### ThingsPanel · role

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/role` | 源码：role.go:25 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/role` | 源码：role.go:16 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/role` | 源码：role.go:22 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/role/:id` | 源码：role.go:19 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · scene

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/scene` | 源码：scene.go:21 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/scene` | 源码：scene.go:15 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/scene` | 源码：scene.go:27 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/scene/:id` | 源码：scene.go:18 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/scene/active/:id` | 源码：scene.go:30 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/scene/detail/:id` | 源码：scene.go:24 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/scene/log` | 源码：scene.go:33 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · scene_automations

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `POST` | `/api/v1/scene_automations` | 源码：scene_automations.go:15 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/scene_automations` | 源码：scene_automations.go:21 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/scene_automations/:id` | 源码：scene_automations.go:18 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/scene_automations/alarm` | 源码：scene_automations.go:36 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/scene_automations/detail/:id` | 源码：scene_automations.go:30 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/scene_automations/list` | 源码：scene_automations.go:27 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/scene_automations/log` | 源码：scene_automations.go:33 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/scene_automations/switch/:id` | 源码：scene_automations.go:24 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · service

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `POST` | `/api/v1/service` | 源码：service_plugin.go:15 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/service` | 源码：service_plugin.go:21 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/service/:id` | 源码：service_plugin.go:23 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/service/access` | 源码：service_plugin.go:30 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/service/access` | 源码：service_plugin.go:34 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/service/access/:id` | 源码：service_plugin.go:36 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/service/access/device/list` | 源码：service_plugin.go:40 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/service/access/list` | 源码：service_plugin.go:32 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/service/access/voucher/form` | 源码：service_plugin.go:38 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/service/detail/:id` | 源码：service_plugin.go:19 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/service/list` | 源码：service_plugin.go:17 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/service/plugin/info` | 源码：service_plugin.go:27 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/service/plugin/select` | 源码：service_plugin.go:25 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · sys_function

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/sys_function` | 源码：router_init.go:106 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/sys_function/:id` | 源码：sys_function.go:15 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · sys_version

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/sys_version` | 源码：router_init.go:122 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · system

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/system/metrics/current` | 获取当前系统指标 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/system/metrics/history` | 获取系统指标历史数据 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · systime

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/systime` | 源码：router_init.go:104 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · telemetry

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `DELETE` | `/api/v1/telemetry/datas` | 源码：telemetry_data.go:33 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/telemetry/datas/current/:id` | 源码：telemetry_data.go:16 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/telemetry/datas/current/detail/:id` | 源码：telemetry_data.go:22 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/telemetry/datas/current/keys` | 源码：telemetry_data.go:19 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/telemetry/datas/current/keys/ws` | 源码：router_init.go:101 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/telemetry/datas/current/ws` | 源码：router_init.go:95 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/telemetry/datas/history` | 源码：telemetry_data.go:25 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/telemetry/datas/history/page` | 源码：telemetry_data.go:30 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/telemetry/datas/history/pagination` | 源码：telemetry_data.go:28 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/telemetry/datas/msg/count` | 源码：telemetry_data.go:60 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/telemetry/datas/pub` | 源码：telemetry_data.go:45 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/telemetry/datas/set/logs` | 源码：telemetry_data.go:42 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/telemetry/datas/simulation` | 源码：telemetry_data.go:48 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/telemetry/datas/simulation` | 源码：telemetry_data.go:51 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/telemetry/datas/simulation/init` | 源码：telemetry_data.go:54 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/telemetry/datas/simulation/send` | 源码：telemetry_data.go:57 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/telemetry/datas/statistic` | 源码：telemetry_data.go:36 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/telemetry/datas/statistic/batch` | 源码：telemetry_data.go:39 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · tenant

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `POST` | `/api/v1/tenant/email/register` | 源码：router_init.go:108 | 公开/专用凭证（逐项核实） |
| [x] | `GET` | `/api/v1/tenant/has-admin` | 源码：router_init.go:110 | 公开/专用凭证（逐项核实） |
| [x] | `POST` | `/api/v1/tenant/market-register` | 源码：router_init.go:116 | 公开/专用凭证（逐项核实） |
| [x] | `GET` | `/api/v1/tenant/setup-state` | 源码：router_init.go:112 | 公开/专用凭证（逐项核实） |
| [x] | `POST` | `/api/v1/tenant/super-admin/init` | 源码：router_init.go:114 | 公开/专用凭证（逐项核实） |

### ThingsPanel · ui_elements

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/ui_elements` | 源码：sys_ui_elements.go:25 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/ui_elements` | 源码：sys_ui_elements.go:16 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/ui_elements` | 源码：sys_ui_elements.go:22 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/ui_elements/:id` | 源码：sys_ui_elements.go:19 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/ui_elements/menu` | 源码：sys_ui_elements.go:28 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/ui_elements/select/form` | 源码：sys_ui_elements.go:31 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · user

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/user` | 源码：sys_user.go:22 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/user` | 源码：sys_user.go:24 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/user` | 源码：sys_user.go:25 | JWT + Casbin（按账号实际权限） |
| [x] | `DELETE` | `/api/v1/user/:id` | 源码：sys_user.go:26 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/user/:id` | 源码：sys_user.go:27 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/user/address/:id` | 源码：sys_user.go:31 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/user/detail` | 源码：sys_user.go:16 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/user/logout` | 源码：sys_user.go:18 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/user/refresh` | 源码：sys_user.go:19 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/user/selector` | 源码：sys_user.go:37 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/user/tenant/id` | 源码：sys_user.go:34 | JWT + Casbin（按账号实际权限） |
| [x] | `GET` | `/api/v1/user/tenant/statistics` | 源码：sys_user.go:23 | JWT + Casbin（按账号实际权限） |
| [x] | `POST` | `/api/v1/user/transform` | 源码：sys_user.go:28 | JWT + Casbin（按账号实际权限） |
| [x] | `PUT` | `/api/v1/user/update` | 源码：sys_user.go:17 | JWT + Casbin（按账号实际权限） |

### ThingsPanel · verification

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/v1/verification/code` | 源码：router_init.go:91 | 公开/专用凭证（逐项核实） |

### ThingsVis · internal

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `POST` | `/api/internal/market-dashboards/import` | ThingsVis route: internal/market-dashboards/import/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `POST` | `/api/internal/market-dashboards/{dashboardId}/analyze` | ThingsVis route: internal/market-dashboards/[dashboardId]/analyze/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `POST` | `/api/internal/market-dashboards/{dashboardId}/export` | ThingsVis route: internal/market-dashboards/[dashboardId]/export/route.ts | JWT/Bearer + tenant/role scope |

### ThingsVis · open

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `GET` | `/api/open/v1/apps` | ThingsVis route: open/v1/apps/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `POST` | `/api/open/v1/apps` | ThingsVis route: open/v1/apps/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `DELETE` | `/api/open/v1/apps/{appId}/keys` | ThingsVis route: open/v1/apps/[appId]/keys/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `POST` | `/api/open/v1/apps/{appId}/keys` | ThingsVis route: open/v1/apps/[appId]/keys/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `GET` | `/api/open/v1/dashboards` | ThingsVis route: open/v1/dashboards/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `POST` | `/api/open/v1/dashboards` | ThingsVis route: open/v1/dashboards/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `DELETE` | `/api/open/v1/dashboards/{id}` | ThingsVis route: open/v1/dashboards/[id]/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `GET` | `/api/open/v1/dashboards/{id}` | ThingsVis route: open/v1/dashboards/[id]/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `PUT` | `/api/open/v1/dashboards/{id}` | ThingsVis route: open/v1/dashboards/[id]/route.ts | JWT/Bearer + tenant/role scope |

### ThingsVis · v1

| 状态 | 方法 | 路径 | 语义/源码证据 | 身份边界 |
|---|---|---|---|---|
| [x] | `POST` | `/api/v1/auth/login` | ThingsVis route: v1/auth/login/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `GET` | `/api/v1/auth/me` | ThingsVis route: v1/auth/me/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `POST` | `/api/v1/auth/register` | ThingsVis route: v1/auth/register/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `POST` | `/api/v1/auth/sso` | ThingsVis route: v1/auth/sso/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `GET` | `/api/v1/dashboards` | ThingsVis route: v1/dashboards/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `POST` | `/api/v1/dashboards` | ThingsVis route: v1/dashboards/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `GET` | `/api/v1/dashboards/home` | ThingsVis route: v1/dashboards/home/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `POST` | `/api/v1/dashboards/import` | ThingsVis route: v1/dashboards/import/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `DELETE` | `/api/v1/dashboards/{id}` | ThingsVis route: v1/dashboards/[id]/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `GET` | `/api/v1/dashboards/{id}` | ThingsVis route: v1/dashboards/[id]/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `PUT` | `/api/v1/dashboards/{id}` | ThingsVis route: v1/dashboards/[id]/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `POST` | `/api/v1/dashboards/{id}/apply-super-admin-home` | ThingsVis route: v1/dashboards/[id]/apply-super-admin-home/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `POST` | `/api/v1/dashboards/{id}/duplicate` | ThingsVis route: v1/dashboards/[id]/duplicate/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `GET` | `/api/v1/dashboards/{id}/export` | ThingsVis route: v1/dashboards/[id]/export/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `DELETE` | `/api/v1/dashboards/{id}/publish` | ThingsVis route: v1/dashboards/[id]/publish/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `POST` | `/api/v1/dashboards/{id}/publish` | ThingsVis route: v1/dashboards/[id]/publish/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `DELETE` | `/api/v1/dashboards/{id}/set-homepage` | ThingsVis route: v1/dashboards/[id]/set-homepage/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `POST` | `/api/v1/dashboards/{id}/set-homepage` | ThingsVis route: v1/dashboards/[id]/set-homepage/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `DELETE` | `/api/v1/dashboards/{id}/share` | ThingsVis route: v1/dashboards/[id]/share/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `GET` | `/api/v1/dashboards/{id}/share` | ThingsVis route: v1/dashboards/[id]/share/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `POST` | `/api/v1/dashboards/{id}/share` | ThingsVis route: v1/dashboards/[id]/share/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `GET` | `/api/v1/dashboards/{id}/thumbnail` | ThingsVis route: v1/dashboards/[id]/thumbnail/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `GET` | `/api/v1/dashboards/{id}/validate-share` | ThingsVis route: v1/dashboards/[id]/validate-share/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `GET` | `/api/v1/datasources` | ThingsVis route: v1/datasources/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `POST` | `/api/v1/datasources` | ThingsVis route: v1/datasources/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `DELETE` | `/api/v1/datasources/{id}` | ThingsVis route: v1/datasources/[id]/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `GET` | `/api/v1/datasources/{id}` | ThingsVis route: v1/datasources/[id]/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `PUT` | `/api/v1/datasources/{id}` | ThingsVis route: v1/datasources/[id]/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `GET` | `/api/v1/health` | ThingsVis route: v1/health/route.ts | public health check |
| [x] | `GET` | `/api/v1/projects` | ThingsVis route: v1/projects/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `POST` | `/api/v1/projects` | ThingsVis route: v1/projects/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `DELETE` | `/api/v1/projects/{id}` | ThingsVis route: v1/projects/[id]/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `GET` | `/api/v1/projects/{id}` | ThingsVis route: v1/projects/[id]/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `PUT` | `/api/v1/projects/{id}` | ThingsVis route: v1/projects/[id]/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `POST` | `/api/v1/public/assets/import` | ThingsVis route: v1/public/assets/import/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `GET` | `/api/v1/public/assets/proxy` | ThingsVis route: v1/public/assets/proxy/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `GET` | `/api/v1/public/dashboard/{token}` | ThingsVis route: v1/public/dashboard/[token]/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `GET` | `/api/v1/uploads` | ThingsVis route: v1/uploads/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `POST` | `/api/v1/uploads` | ThingsVis route: v1/uploads/route.ts | JWT/Bearer + tenant/role scope |
| [x] | `GET` | `/api/v1/uploads/*filename` | ThingsVis route: v1/uploads/[...filename]/route.ts | JWT/Bearer + tenant/role scope |

## 角色验收矩阵

> 历史矩阵曾验证三个 authority；用户确认 community 不提供 TENANT_USER 后，本轮代码已拒绝该角色登录和携带旧 JWT，原数据库行未删除。本机 MCP profile 只保留租户 A、SYS_ADMIN、租户 B 三种有效 community 身份，三者经 MCP 读取个人信息业务码均为 200。新 community 拒绝规则待后端编译/部署验证。

- [x] 超级管理员：真实 SYS_ADMIN JWT 经 MCP 读取个人信息、系统指标、全局设备列表和另外两个租户的示例设备详情成功。
- [x] 租户管理员：真实 TENANT_ADMIN JWT 经 MCP 读取个人信息成功；访问超管专属系统指标返回业务码 201001。
- [x] Community 角色边界：TENANT_ADMIN 创建 TENANT_USER、TENANT_USER 登录、TENANT_USER 旧 JWT API 请求均在源码层拒绝；运行时负向验证待做。
- [x] 租户范围：tenant-ha 与 tenant@ 示例设备在历史矩阵中互相隔离；SYS_ADMIN 可读全局设备列表与跨租户详情。community TENANT_ADMIN 仍只读本租户。
- [x] ThingsVis：SSO 向 ThingsPanel 验证 JWT 并按 authority 派生身份；本轮只允许 SYS_ADMIN/TENANT_ADMIN，TENANT_USER 不映射；本轮测试待运行。

## 每个工具测试门槛

- [x] 每个 MCP 工具有命名、参数、路径替换、请求体、响应与错误语义测试；FastMCP 调用覆盖 363/363 工具。
- [x] 认证/权限：真实角色允许/拒绝矩阵覆盖系统指标和设备租户范围；token 轮换、无效 token 及 HTTP 200 业务错误有回归测试。
- [x] 写入/删除/控制/发布工具要求显式 `confirmed=true`；所有 write tool dispatch 在假客户端覆盖测试中验证，本轮不向共享开发数据发送实际写请求。
- [x] 上传下载、SSE/WebSocket、内部 API 用有界适配器/明确配置错误覆盖，并审计排除 3 条基础设施路由。
- [x] 日志与文档不包含 token、API Key、密码或无关个人数据。

## 验收计数

- 当前源码/文档操作清单：436（314 backend router + 52 ThingsVis + 70 去重后的当前未注册文档操作）
- 已实现并启用 API 工具：363（ThingsPanel 311、ThingsVis 52）；另有 3 条基础设施路由明确排除。
- 已通过 FastMCP 精确路由/路径参数分派契约测试：363/363；MCP Python 测试 18 项通过。
- 已实际经 MCP 调用 ThingsVis GET 工具：20/20；8 个 200、8 个 404、2 个 400，2 个缺少专用 Open API Key 的工具返回结构化配置错误。
- 已本地授权 API smoke：ThingsVis OWNER 的 `/auth/me`、`/projects`、`/dashboards` 均 200；ThingsPanel 四个账号登录成功，SYS_ADMIN/TENANT_ADMIN/TENANT_USER 的个人信息经 MCP 均返回业务码 200；超管系统指标允许，另外两种角色拒绝（业务码 201001）；超管可读全局设备列表和跨租户详情，租户管理员/用户仍被 201001 拒绝跨租户详情。
- API 清单：已从 backend router AST 和 ThingsVis route handlers 生成，并与 328 个 Apifox API 页面、Swagger 导出逐项对照；含 66 个 Apifox-only route 的审计记录和 57 个 source-only route。
- 最终状态：MCP 覆盖、工具契约测试、超管跨租户设备读取、Codex 本机配置已完成；community 角色限制代码已修改、待构建和负向运行验证；ThingsVis SSO community 两角色规则待测试。本机 MCP 写/控制工具已配置逐次批准，真实写入不在共享开发数据执行。
