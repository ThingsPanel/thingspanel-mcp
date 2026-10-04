# 变更清单、风险评估与 WorkBuddy 上架差距

日期：2026-09-26

## 1. 改了哪些代码，为什么改

| 仓库/文件 | 改动 | 必须修改的原因 |
|---|---|---|
| MCP `src/thingspanel_mcp/api_manifest.json`、`api_tools.py`、`server.py` | 从当前 ThingsPanel router 与 ThingsVis handlers 为 363 个接口生成独立 allow-listed 工具；加上旧有 13 个工具，启动时共 376 个。 | 原来只有 13 个概括工具，无法覆盖本次审计到的真实 API，也无法用同一接口验证准确路径、认证类别和参数。 |
| MCP `api_client.py`、`config.py`、`main.py` | 支持 ThingsPanel JWT/API Key、多 profile、ThingsVis session/Open API Key、流式接口、上传路径参数及结构化业务错误；移除会打印 API Key 前缀的日志。 | 不同服务的认证方式并不相同；HTTP 200 也可能携带无权限等业务错误；凭证不得进入普通日志。 |
| MCP `pyproject.toml` | 增加 `websockets`；将 `mcp` 约束为 `>=1.2,<2.0`；把 API manifest 打包进 wheel。 | 当前代码使用 MCP SDK 1.x 的 `FastMCP`；无上限会安装 2.x 并在启动时报模块错误；缺少 package-data 时安装包找不到 API 清单。 |
| Backend `internal/service/device.go`、`internal/dal/devices.go`、`internal/dal/r_group_device.go`、`internal/model/devices.http.go` | 仅 SYS_ADMIN 可列出和读取跨租户设备；租户角色仍按 tenant_id 限定。 | 实测发现产品明确要求超管跨租户读取，但原服务/DAO 在列表、详情和分组路径都按当前租户过滤。 |
| Backend `internal/service/sys_user.go`、`internal/middleware/jwt_auth.go`、`internal/dal/users.go`、`internal/dal/ui_elements.go`、`pkg/authz/community_roles.go` | 社区版仅接受 SYS_ADMIN、TENANT_ADMIN；TENANT_ADMIN 不能创建 TENANT_USER；TENANT_USER 登录与旧 JWT 请求被拒绝；租户管理员端的用户列表/管理菜单/选择器不再展示子用户，直接按 ID 读/改/删/切换旧子用户也会被拒绝。 | 当前 community 源码保留了企业版子用户创建、管理、选择与授权路径，和“社区版只有租户管理员、无租户下用户”的产品边界冲突。 |
| ThingsVis `apps/server/src/lib/thingspanel-sso.ts`、`thingspanel-sso.test.ts`、`auth/sso/route.ts`、`validators/auth.ts` | SSO 只根据 ThingsPanel 服务端校验结果签发身份；无 tenant id 的 SYS_ADMIN 映射到 `sys-admin`；community 不再把 TENANT_USER 映射为 EDITOR。 | 客户端提交的身份不能成为授权依据；SYS_ADMIN 没有租户 ID；TENANT_USER 不属于社区版身份。 |
| Frontend `src/typings/api.d.ts`、`typings/business.d.ts`、`constants/business.ts`、`views/_builtin/login/modules/components/other-account.vue`、`utils/thingsvis/thingsvis-auth.ts` | 社区版角色类型与登录示例只保留 SYS_ADMIN/TENANT_ADMIN；不再把未知身份降级为 ThingsVis 编辑者。 | 前端原有类型、快速登录和 SSO 默认分支会让用户误以为 TENANT_USER 是社区版受支持角色。 |
| MCP README 与 `docs/*` | 增加部署说明、接口差异清单、全局任务进度、错误记录、变更风险及 WorkBuddy 发布差距。 | 本次涉及 API 覆盖、身份边界与协议差异，需要给维护者留下可审阅的事实依据和回归范围。 |

本次保留了此前工作树内已有的其他本地改动，没有覆盖或还原它们。未提交 Git commit，也没有对共享开发数据执行设备创建、删除或控制。

## 2. 错误与语义修正逐项说明

表中 `(a)` 对应原先错误及正确语义，`(b)` 对应修正后的现状和残余后果，`(c)` 对应收益。开发过程里的命令/路径探测错误也保留在表里，避免把过程性错误伪装成产品缺陷。

| ID | (a) 犯的错、正确做法 | (b) 现在怎么样、可能后果 | (c) 改后的收益 | 风险范围 |
|---|---|---|---|---|
| E-001 | 把前端 5002 的 SPA 地址和 `/api/v1/health` 当作后端 API；应按代理前缀与 router 定位服务。 | 已用真实代理和 `/health` 区分前后端；只影响 API 探测结论。 | 后续探测命中正确服务。 | 低：仅本机开发验证。 |
| E-002 | 把 ThingsPanel `/board` 和 ThingsVis dashboard 当成同一服务或旧路由；应分开按各自源码注册。 | manifest 保留 ThingsPanel board 工具，ThingsVis 单独按 handler 注册。 | 避免将相同名词错误映射到另一套身份/路径。 | 低：接口覆盖与调用准确性。 |
| E-003 | 旧示例含疑似真实 API Key，CLI 还会打印凭证前缀；正确做法是占位配置并禁止记录秘密。 | 当前代码/文档不输出密钥；若历史发布密钥是真实的，仍需凭证持有人轮换。 | 降低提交记录、终端和支持日志泄漏风险。 | 中：仅影响曾经公开/分发过的真实旧凭证。 |
| E-004 | 误以为只支持 `x-token`；实际还支持 `x-api-key`，但 API Key 代表 TENANT_ADMIN，不能代替超管或企业子用户。 | profile 支持 JWT/API Key，真实授权仍由服务端身份决定；community 现在仅接受两个社区角色。 | 认证方式与身份权限分开，避免把 API Key 权限夸大。 | 中：调用者必须为目标租户配置正确凭证。 |
| E-005 | 初版 ThingsVis SSO 信任请求体内 userInfo/role；应通过服务端校验平台 JWT 后建立身份。 | 当前 ThingsVis 按后端 authority/ID/tenant 签发 SSO 身份，失败即拒绝。 | 防止伪造超管、编辑者或跨租户身份。 | 高：错误会阻止登录；成功时仍按 ThingsVis 的租户映射规则创建/更新账户。 |
| E-006 | zsh 中未引用含 `?` 的 URL 被当作 glob；应引用完整 URL。 | 已重新请求并确认网络返回，与应用行为区分。 | 避免把未执行的探测误报为接口故障。 | 低：开发命令。 |
| E-007 | 路由审计发现 `POST /device/auth` 在两处注册，最初可能按两条工具处理；应按运行时 method/path 去重。 | MCP 对唯一 method/path 只注册一个工具；Backend 中重复注册源码仍在。 | 避免向模型暴露重复工具。 | 低：Backend 路由维护债务仍存在。 |
| E-008 | 临时脚本导入全局安装包，读到旧的 13 个工具；应在当前源码/安装环境检查。 | 以当前仓库 manifest 与 FastMCP 初始化结果为准，当前 runtime 列出 376 个。 | 防止错误地报告工具未注册。 | 低：本机开发环境。 |
| E-009 | 只有命名 profile 时仍强制查 default，造成 KeyError；应只解析本次选中的 profile。 | 命名 profile 已可独立使用；配置不存在时返回明确错误。 | 多租户管理员/超管可明确切换身份。 | 中：默认 profile 仍需由使用者选定，选错 profile 会落入不同租户权限。 |
| E-010 | 用会解码 `%2F` 的 URL 属性验证 path encoding；应核对 raw path。 | `dev/1` 被编码成单个路径段，防止路径穿越。 | 路径参数不改变 router 层级。 | 低：含斜线的 ID/文件名请求。 |
| E-011 | 初版把 SSE/WebSocket 当作普通 JSON HTTP；应按流协议连接并设读取上限。 | 当前按协议读取，限制消息数和持续时间；超限后读取停止。 | 订阅工具能返回真实事件且资源有界。 | 中：服务端仍可能断开、超时或返回部分消息。 |
| E-012 | 临时检查脚本用错 FastMCP 实例字段；应以当前 SDK 实例字段读取注册表。 | 注册数核对为 376。 | 避免把脚本错误归因为 server 问题。 | 低：验证脚本。 |
| E-013 | 首次测试只用一个 API Key，不能证明三种真实角色边界；应使用有效服务端 JWT 做只读角色矩阵。 | 历史测试得到 SYS_ADMIN、TENANT_ADMIN、TENANT_USER；本轮社区规则收紧后，TENANT_USER 账号被拒绝，数据库旧记录未删除。 | 角色与跨租户结果来自实际后端，不依赖 MCP 自报 role。 | 中高：旧 TENANT_USER 账号无法继续登录；租户级数据行仍保留，需另行决定迁移/清理。 |
| E-014 | 只做 ThingsVis mock 分派，不能证明本地 GET 到达服务；应经 MCP 用不存在资源 ID 做只读探测。 | 20 个历史 GET 基线为 8 个 200、8 个资源 404、2 个参数 400、2 个缺专用 Key；不是本轮重跑结果。 | 区分服务连通性、数据不存在与配置缺失。 | 低中：错误 Key 仍无法验证 Open API。 |
| E-015 | 路径参数提取只覆盖 `:id`，遗漏 `*filename`；应覆盖 catch-all 下载路由。 | `:` 与 `*` 都检查必填并编码。 | 下载、上传路径不出现空参数或少一段的问题。 | 低：文件路径参数仍依赖调用者给出正确相对路径。 |
| E-016 | 只按 Apifox 数量推断 API 覆盖，忽略文档与 router 漂移；应对比唯一 method/path 并逐项审计。 | 436 项总清单及 Apifox 差异已记录；router-only 操作保留，未注册项另有理由。 | 让覆盖率能复查、能更新。 | 中：文档差异随上游版本变化，需要每次发布前重跑审计。 |
| E-017 | 按 `/api/open/` 前缀把所有 ThingsVis handler 当 API Key；应依据 handler 认证方式分类。 | apps/keys 使用 session JWT；dashboard Open API 使用专用 Key。 | 避免把 session token 当作 dashboard key 误调。 | 中：Open API Key 仍须由用户单独提供。 |
| E-018 | 只看 HTTP 状态，把 HTTP 200 + 业务码 201001 当成功；正确语义是检查响应 envelope 的 code。 | 业务码非 200 现在返回 `ok:false`；若 200 响应缺少业务 code，则按常规 HTTP 响应处理。 | 无权限等错误不会假装为成功。 | 低中：不同服务 envelope 需保持独立解析规则。 |
| E-019 | ThingsVis 本地无上游地址配置导致 SSO 503；应配置 server-to-server verifier 地址。 | 历史测试在本机 ignored `.env` 配置后成功，本轮未重新启动/验收 ThingsVis。 | SSO 只向明确配置的后端验证。 | 中：换环境部署时若漏配，会拒发 ThingsVis token。 |
| E-020 | 假设 SYS_ADMIN 一定有 tenant id；实际系统角色无 tenant id。 | 仅已验证的 SYS_ADMIN 映射到稳定 ThingsVis `sys-admin`；租户角色仍需真实 tenant id。 | 系统管理员可登录 ThingsVis，租户之间不混入系统租户。 | 中：`sys-admin` 是 ThingsVis 内部空间标识，需在多环境保持一致。 |
| E-021 | 原设备列表/详情/分组查询把 SYS_ADMIN 也限制到单 tenant；应只对服务端 authority 为 SYS_ADMIN 的读路径放宽。 | SYS_ADMIN 可全租户读取；TENANT_ADMIN 与历史 TENANT_USER 在修正规则前被验证为只能读本租户。 | 实现用户确认的超管跨租户读取，同时保留租户隔离。 | 高：超管能看到各租户设备信息；任何超管 token 泄漏都会扩大数据暴露面。 |
| E-022 | community 源码仍让租户管理员创建 TENANT_USER、接受其登录并在 SSO 中授予 EDITOR；正确做法是社区版只有 SYS_ADMIN/TENANT_ADMIN，企业版用户能力应留在企业版。 | 后端创建、登录、JWT 中间件都拒绝租户用户；ThingsVis community SSO 拒绝；前端删掉角色类型和演示账号。旧数据库记录未删除。 | API、token、中间件、SSO 和 UI 边界一致，避免把 enterprise 子用户能力误带入 community。 | 高：已有 TENANT_USER 不能登录/调用 API；若未来企业版共用此代码需在企业版分支/edition gate 恢复该角色，不能直接 cherry-pick。 |
| E-023 | `mcp>=1.2` 允许安装不兼容的 MCP SDK 2.x；正确做法是锁定 `FastMCP` 所依赖的大版本，并实际启动检查。 | 本机初装 2.2.0 启动失败；将上限改为 `<2.0` 后安装 1.30.0，MCP 握手成功并列出 376 个工具。 | 干净环境能够启动，不会发布一个依赖解析成功但运行失败的包。 | 低中：未来升级 SDK 2.x 前必须迁移 API 并重新验证。 |
| E-024 | 只检查 MCP 握手，忽略默认 URL 的 HTTP→HTTPS 重定向和 HTTP 200 包装业务错误。 | 已把本机 `~/.thingspanel/config.json` 的默认 URL 指到正在运行的 `http://localhost:9999`；MCP 三个 profile 的只读个人信息返回 200。 | Codex 运行的 MCP 现在实际连到本地 ThingsPanel，默认身份为租户 A，另有超管和租户 B profile。 | 中高：凭证以 JWT 形式保存在权限为 0600 的本机配置中；JWT 有有效期；超管 profile 有跨租户读取/写入 API 的能力。 |

## 3. 负面影响、可靠性与收益

| 变更 | 负面影响 | 风险范围 | 缓解方式/回退条件 |
|---|---|---|---|
| 超管跨租户设备只读 | SYS_ADMIN 工具调用会看到所有租户设备信息；若角色签发或 token 泄漏，影响从单租户扩大到全平台。 | 高；限定于受认证 SYS_ADMIN 的设备列表、详情、分组路径读取。没有放宽租户管理员。 | 超管只读范围可在 `canReadTenantDevice` 与列表 tenant 过滤恢复；回退会重新使超管跨租户详情失败。 |
| 社区版移除 TENANT_USER | 现有 tenant user 账号登录失败、租户管理员不能再查询/管理/选择这些账号；企业版依赖这些代码时不能把 community 改动原样同步过去。旧用户表行还在。 | 高；仅 community backend、community frontend、该 ThingsVis SSO integration。 | 回退须一次性恢复创建、登录、JWT 授权、菜单、用户列表/选择器、前端角色和 ThingsVis SSO 映射，不能只放开其中一层。先备份/评估旧用户行再决定数据迁移。 |
| 本机 Codex 的 3 个 profile token | 配置文件可访问者能以租户管理员或 SYS_ADMIN 调用工具；token 失效后需要重新登录并替换。 | 高；仅当前 macOS 用户，配置文件权限 0600；默认 profile 是租户 A，超管需显式 `profile="superadmin"`。 | 删除 `~/.thingspanel/config.json` 中相关 profile 并在 Codex 移除 MCP server。超管 profile 只在必要的只读工作中选择。 |
| 376 个 MCP 工具、其中 190 个写/控制工具 | 工具量增大模型选错工具的概率，写工具能影响设备、用户、看板等业务资源。 | 中高；工具调用最终由后端权限控制。本机 Codex 已对 190 个写/控制工具配置 `approval_mode="approve"`，且服务端要求 `confirmed=true`。 | 降低 WorkBuddy 上架工具面；提供只读精简 profile；发布前用 disposable tenant 做写测试。 |
| MCP SDK `<2` 约束 | 不能自动获得 SDK 2.x 新功能。 | 低；仅 Python 依赖版本。 | 做完 FastMCP→MCPServer 迁移并跑协议握手后再放宽。 |
| 验证范围 | 本轮运行 Backend `go build`、ThingsVis `tsc --noEmit`、MCP handshake 与三个 profile 只读检查；Frontend `vue-tsc` 失败，输出存在大量跨仓库类型错误；未运行新的后端/SSO测试套件。 | 中；Backend 新 community guard 已编译并部署到本地，TENANT_USER 负向运行验证仍未执行；Frontend 错误无本轮前基线，不能判定都来自旧代码。 | 发布前运行后端/SSO授权测试并对 TENANT_USER 登录做负向验证；修复或归档前端完整类型检查诊断。 |

## 4. 本地 Codex 配置

- 已用 `uv tool install --editable` 将仓库安装成本机命令：`/Users/junhong/.local/bin/thingspanel-mcp`。
- 已添加全局 Codex MCP server `thingspanel`，transport 为 stdio；本机 Codex 配置写在 `~/.codex/config.toml`。
- 通过真实 MCP client initialize/list-tools 握手，启动成功并列出 376 个工具；只读调用确认本地 default/TENANT_ADMIN、superadmin/SYS_ADMIN、tenant_b/TENANT_ADMIN 三个 profile 可返回用户信息。
- 用户级 `~/.thingspanel/config.json` 指向本机 backend `http://localhost:9999`，包含 3 个 profile 的 JWT，权限设为 `0600`；密码未保存到配置或仓库。默认 profile 是租户 A；跨租户读取需明确设置 `profile="superadmin"`。
- 已在 Codex 配置中对 186 个生成的非 GET 工具和 4 个旧控制工具共 190 个写/控制工具设置 `approval_mode="approve"`。Codex 桌面可能需要重启/刷新 MCP 才显示新 server 和确认提示。
- 本机 MCP 是 stdio 按需进程，不是后台常驻 daemon；Codex 调用时启动，关闭连接后退出。

配置来源和三类角色映射请保密，不在报告复制实际 JWT、密码或 API Key。

## 5. Skill 是否必需

Codex 调 MCP 不需要 Skill：MCP 已将工具名、参数和说明注册给客户端。Skill 是说明“什么场景选什么工具、先查再写、如何指定 profile、哪些操作需人工批准”的可选工作流指南。

WorkBuddy 官方连接器规范也说明 MCP 已提供标准工具描述时 Skill 可选；但本 MCP 有 363 个 API 工具和多种认证/高风险写操作，市场连接器建议附带 Skill，指导核心工具用途、参数、认证、常见错误和写操作确认规则。Skill 不会替代后端鉴权，也不会把 `confirmed=true` 变成人工批准。

## 6. WorkBuddy 发布上架目前还差什么

截至 2026-09-26，官方文档区分两种行为：

1. **本机自定义 MCP**：可在 WorkBuddy MCP 配置里填写 stdio 命令，开发/个人验证时可不发布市场。
2. **WorkBuddy 连接器市场上架**：需按连接器规范打包目录并提交 WorkBuddy 团队审核；审核通过后才进入市场。不能把“本机 Codex 配置成功”当作“市场已发布”。

| 上架项目 | 当前状态 | 剩余工作/风险 |
|---|---|---|
| 连接器目录 | 未创建 | 至少要有 `connector-meta.json`、`mcp.json`、`icon.svg`；Skill 与 token schema 视认证模式加入。 |
| 安装运行时 | 本机已用 uv 安装 | WorkBuddy 用户机器须能运行 Python MCP；可先用 `uvx --from thingspanel-mcp==<新版本>` 做 stdio 安装验证，但 PyPI 当前最新为 0.1.8，仓库版本为 0.1.6 且含未发布改动，须先提升版本并发布 PyPI 包。不能在 connector manifest 指向不存在版本。 |
| 发布版本 | 未发布本轮代码 | PyPI 0.1.8 已占用；本轮代码不能以 0.1.6 覆盖，需定新版本、核对源码/许可证/README/依赖并由维护者发布。 |
| 认证表单 | 当前由本机配置文件读取 profile | WorkBuddy connector 应用 `auth_mode="token"` + `token-schema.json`，让用户在本机填写 ThingsPanel API Key 与平台 Base URL；不能把当前机器的 JWT/API Key 写进包。 |
| Server 传输 | 本机 stdio 正常 | WorkBuddy 官方支持本地 stdio；若改成远程托管则须 HTTPS + SSE 或 streamable HTTP。本仓库现在有 stdio/SSE，没有 streamable HTTP；若提交远程方案还需补传输与部署。 |
| 工具面安全 | 363 API + 13 旧工具 | 公开连接器把 376 个工具一次性暴露会造成工具选择噪声和误写风险。应做只读/常用工具精简、禁用高风险工具或拆分连接器；至少对写/命令/删除提供明确人工确认。 |
| Skill/说明/示例 | 有 README 与 API 清单，无 WorkBuddy connector Skill | 建议提供中英文说明、2–5 个示例、profile/认证指引、常见错误和确认规则；MCP 的标准参数描述已满足基础调用，但 Skill 能减少 363 个工具间误选。 |
| 图标与元数据 | 缺少 | 需要唯一 `source`（小写 kebab-case）、版本、中英文名称/描述、示例和图标。 |
| 凭证和隐私审核 | 本地配置已保护 | 不得把真实 token 放入打包文件、Skill 或例子；连接器需要最小权限。高权限超管连接器尤其需要缩窄可调用权限，并确认 WorkBuddy 上架所需主体、隐私和开发者认证。 |
| 上架提交 | 尚未提交 | 官方流程要求提交连接器包审核；批准后进入市场，后续更改需重新审核。 |

### 上架方案选择

| 方案 | 优点 | 代价/问题 | 推荐用途 |
|---|---|---|---|
| A. WorkBuddy 自定义 stdio MCP | 最快；不需要市场审核或公网 MCP 服务。 | 用户本机要有兼容 Python/uv；必须逐用户填写凭证；目前 PyPI 最新安装包缺少本轮改动。 | 小范围内部试用/验证。 |
| B. PyPI 包 + WorkBuddy 连接器市场（stdio） | 用户安装简单；凭证可以留在本机；复用已有社区 MCP。 | 先发新的 PyPI 版本、完成连接器元数据/图标/token 表单/Skill/安全精简、再提交审核；Python/uv 环境兼容仍需验证。 | 推荐的首个公开发布路径，前提是工具面做最小权限收敛。 |
| C. HTTPS 远程 MCP 服务 | 用户不用安装 Python/uv；可集中管理更新。 | 需补 streamable HTTP 或稳定 SSE 部署、TLS、OAuth/用户隔离、租户授权代理和运维可用性；不能共享单个超管 token。 | 企业级托管服务，工作量最高。 |

**建议顺序：**先保留本地 Codex 版本完成只读/写权限回归；同时将 WorkBuddy 公开包定为“租户管理员只读工具优先”的最小连接器，再补 PyPI 发布版本和 connector bundle。不要把本机 superadmin profile 打包或设为 WorkBuddy 市场默认身份。

### 官方资料

- [WorkBuddy 开放平台连接器规范](https://open.workbuddy.cn/docs/connector)：目录、MCP 传输、安全、用户自填 Token、Skill、上架检查与审核。
- [WorkBuddy MCP 配置指南](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/MCP-Guide)：用户级 `~/.workbuddy/mcp.json`、本机 MCP 配置和使用方式。
- [ThingsPanel MCP 当前 PyPI 发行记录](https://pypi.org/project/thingspanel-mcp/)：当前已有公开发行 0.1.8；本地仓库版本 0.1.6 与公开发行不同。

## 7. 用户、客户、市场和商业价值

- 用户可以在 Codex 里用自然语言读取设备、遥测、告警与看板数据；租户管理员默认留在单租户权限内，超管需显式选择超管 profile。
- 社区版的登录、菜单、用户列表和 ThingsVis SSO 现在都遵守同一双角色边界，减少把企业版子用户能力误配置给社区客户的支持问题。
- WorkBuddy 连接器市场可把 ThingsPanel IoT API 接入到更广的桌面 Agent 使用场景，带来一个潜在集成分发入口；这属于产品机会推断，不代表市场审核或流量保证。
- 发布包必须解决 PyPI 版本、每用户凭证、运行时依赖、工具数量与高危写调用门槛；如果把系统管理员凭证或 376 个未收敛的工具直接默认开放，用户风险和后续支持成本会抵消分发收益。
