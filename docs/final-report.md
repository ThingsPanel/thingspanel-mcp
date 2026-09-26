# ThingsPanel / ThingsVis MCP 完成报告

日期：2026-09-26

## 修改思路

以当前 backend router 与 ThingsVis route handler 为可运行 API 的准据，Apifox/Swagger 用于发现文档差异。为每个启用接口注册独立 allow-listed MCP 工具；角色始终由后端 token 决定。真实角色验证发现 HTTP 200 包装业务错误、SYS_ADMIN 没有 tenant id、SYS_ADMIN 设备读取被错误限制等根因。用户随后确认社区版没有租户子用户，因此本次后续修正 community 的 TENANT_USER 创建/登录/JWT/SSO 边界。

## 覆盖与实现

- API 清单共 436 项：314 个 ThingsPanel router 操作、52 个 ThingsVis handler、70 个仅见于文档的操作；3 个基础设施路由不开放为业务工具。
- 已启用 363 个独立 MCP API 工具：ThingsPanel 311 个，ThingsVis 52 个；原有 13 个工具保留，运行时共 376 个。
- 每个启用工具均由 FastMCP registry test 调用并核对精确 method/path/path params。写工具要求 `confirmed=true`。SSE/WebSocket 有界读取，上传/下载处理 catch-all 路径参数，ThingsVis Open API 区分 session JWT 与 Dashboard 专用 Key。
- Apifox 1.1.6 的 323 个唯一操作中，257 项与 router 精确吻合、66 项当前未注册；另有 57 项 router-only。未注册文档操作已逐项审计并排除。
- ThingsPanel MCP 现在按响应 envelope 的业务 `code` 判定成功：`200` 为成功，其他数值业务码返回 MCP `ok=false`。
- SYS_ADMIN 可以列出所有租户设备并读取跨租户设备详情；当前 community 只允许 TENANT_ADMIN 按本租户读取。该授权判断来自已验证的服务端 authority，MCP 参数不能伪造角色。
- ThingsVis SSO 向 ThingsPanel 服务端验证 JWT，忽略调用者提交的 role/userInfo。Community 只映射 `SYS_ADMIN → SUPER_ADMIN`、`TENANT_ADMIN → TENANT_ADMIN`；TENANT_USER 被拒绝。无 tenant id 的 SYS_ADMIN 映射到稳定系统租户 `sys-admin`；TENANT_ADMIN 必须提供真实 tenant id。

## 账号与场景验证

之前的权限矩阵使用四个本地账号确认三种角色：一个 SYS_ADMIN、两个 TENANT_ADMIN、一个 TENANT_USER。用户确认 community 不支持 TENANT_USER 后，本轮只为三个 community 身份在本机 MCP 配置凭证：租户 A 管理员作为 default、SYS_ADMIN 作为 `superadmin`、另一个租户管理员作为 `tenant_b_admin`。租户用户旧记录未从数据库删除；新代码会拒绝其登录和旧 JWT。

| MCP 场景 | 结果 |
|---|---|
| 本轮 MCP profile 读取个人信息 | 三个有效 community profile 均成功；分别为租户 A、SYS_ADMIN、租户 B |
| 历史系统指标矩阵 | SYS_ADMIN 成功；TENANT_ADMIN/TENANT_USER 返回业务码 `201001`；community 新规则将拒绝 TENANT_USER 登录/携带旧 JWT |
| 设备列表与详情 | SYS_ADMIN 可跨租户读取；租户管理员本租户可读、跨租户返回 `201001` |
| ThingsVis SSO | Community 当前允许 SYS_ADMIN、TENANT_ADMIN 两类；TENANT_USER 拒绝；请求体伪造身份不生效 |
| ThingsVis 只读 API | 20 个 GET 工具逐个经 MCP 调用：8 个 200、8 个对不存在资源返回 404、2 个缺少必需 query 返回 400；2 个 Dashboard Open API 因未配置专用 API Key 返回结构化配置错误 |

## 验证

- MCP Python：18 项通过；363/363 个启用工具通过精确路由分派测试；`compileall` 与 `git diff --check` 通过。
- ThingsVis：SSO helper 测试 5 项通过；`tsc --noEmit` 与 `git diff --check` 通过。
- ThingsPanel backend：`TestCanReadTenantDevice` 通过；`go build` 通过；重启本地 backend 后再次经 MCP 验证 SYS_ADMIN 全局设备列表/跨租户详情成功，其他角色的跨租户详情仍拒绝。
- 前一阶段角色测试的 token 只保存在单次验证进程内，没有写入日志/报告；本轮为 Codex 持久使用另行生成并保存了三个 community JWT profile（见下文），不保存账户密码。
- 本次本地 Codex 接入为让 profile 可用，将三个 community 账号 JWT 存入 `~/.thingspanel/config.json`，权限设为 `0600`；原始密码未写入。JWT 生命周期来自后端签发配置（30 天），过期需要重新获取并更新。报告与仓库不含 token。
- 新的 community 租户用户拒绝规则、本地 package startup fix 本轮未运行测试套件；MCP 协议握手和三种有效 profile 的只读调用已在本轮实际运行。Backend `go build`、ThingsVis `tsc --noEmit` 通过；Frontend `vue-tsc --noEmit --skipLibCheck` 失败，输出有大量跨仓库类型错误（含缺少 Vitest 类型和多个视图/组件错误）。本轮没有修改前的对照基线，不能断言所有错误均是历史错误。

## 验收范围与操作影响

MCP 的 API 覆盖、参数/路由/确认门槛、角色权限代表性矩阵及 ThingsVis 三角色 SSO 已完成。未对共享开发数据执行设备创建、删除、控制或其他业务写操作；这类写工具都经过假客户端逐项调用，并要求显式确认，真实数据变更不属于本次只读角色验收。

ThingsVis SSO 是登录接口，会按设计创建或更新 ThingsVis 映射用户，并为管理员检查/确保默认看板。本次在本机配置忽略文件中设置了 `THINGSPANEL_API_BASE_URL=http://localhost:9999`，未写入仓库；三类测试账号的 SSO 登录已成功。

本机 Codex 已注册全局 `thingspanel` stdio MCP，MCP initialize/list-tools 握手成功并发现 376 个工具；190 个写入/控制工具配置为调用前显式批准。默认 profile 为租户 A；只有明确选择 `profile="superadmin"` 才具备跨租户权限。Codex 桌面可能需要重启或刷新 MCP 列表。本机 MCP 为按需启动的 stdio 子进程，不常驻后台。

## 可复用结论

- ThingsPanel HTTP 状态码不能单独代表业务成功；MCP 必须检查响应体 `code`。
- SYS_ADMIN 与租户角色的范围判断应明确使用服务端 authority；全局读权限不能通过调用参数自报。
- ThingsPanel SYS_ADMIN 没有 tenant id；ThingsVis 必须为系统角色提供独立、稳定的内部 tenant 映射，同时继续要求租户角色使用真实 tenant id。

详细逐项清单见 [`global-task-list.md`](./global-task-list.md)，问题与语义修正记录见 [`error-log.md`](./error-log.md)，Apifox/源码差异见 [`apifox-source-diff.md`](./apifox-source-diff.md)。

文件级变更、负面影响/风险、Skill 需求判断和 WorkBuddy 市场发布剩余项目见 [`change-impact-and-workbuddy.md`](./change-impact-and-workbuddy.md)。
