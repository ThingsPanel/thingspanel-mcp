# Apifox 与当前 ThingsPanel router 差异

> 基于 [Apifox llms.txt](https://s.apifox.cn/87a62ec6-68e5-4590-ac53-8cfe8a8e814b/llms.txt) 及其 328 个 API 页面在线快照生成；method/path 与工作区 backend router AST 清单精确对比。Apifox 页面仅作比对，工具来源仍以当前 router 为准。

## 计数

- Apifox API 页面：328
- Apifox 唯一 method/path：323
- 当前 router 唯一 method/path：314
- 精确匹配：257
- 仅在 Apifox：66（须确认已删除、未注册或由外部服务提供）
- 仅在当前 router：57（源码新接口或文档缺失）

## 仅在 Apifox

这些操作没有当前 backend router 注册证据，因此不生成 ThingsPanel MCP 工具。

| 方法 | Apifox 路径 |
|---|---|
| `DELETE` | `/api/v1/casbin/user/device` |
| `DELETE` | `/api/v1/casbin/user/device_group` |
| `DELETE` | `/api/v1/forwarding/rule/:id` |
| `DELETE` | `/api/v1/forwarding/source/:id` |
| `DELETE` | `/api/v1/forwarding/target/:id` |
| `DELETE` | `/api/v1/product/:id` |
| `DELETE` | `/api/v1/vis/plugin/dashboard/:id` |
| `GET` | `/api/v1/casbin/user/device` |
| `GET` | `/api/v1/casbin/user/device_group` |
| `GET` | `/api/v1/device/batch/template` |
| `GET` | `/api/v1/device/detail/:id/user` |
| `GET` | `/api/v1/device/group/detail/:id/user` |
| `GET` | `/api/v1/device/preRegister` |
| `GET` | `/api/v1/device/preRegister/export` |
| `GET` | `/api/v1/devices/:device_id/data` |
| `GET` | `/api/v1/form/config` |
| `GET` | `/api/v1/forwarding/rule` |
| `GET` | `/api/v1/forwarding/rule/:id` |
| `GET` | `/api/v1/forwarding/script/:id` |
| `GET` | `/api/v1/forwarding/source` |
| `GET` | `/api/v1/forwarding/source/:id` |
| `GET` | `/api/v1/forwarding/target` |
| `GET` | `/api/v1/forwarding/target/:id` |
| `GET` | `/api/v1/health/kafka` |
| `GET` | `/api/v1/open/keys/tenant` |
| `GET` | `/api/v1/plugin/device/list` |
| `GET` | `/api/v1/product` |
| `GET` | `/api/v1/protocol_plugin/device_config_form` |
| `GET` | `/api/v1/vis/plugin/dashboard` |
| `GET` | `/api/v1/vis/plugin/list` |
| `GET` | `/api/v1/vis/plugin/local` |
| `GET` | `/api/v1/vis/plugin/share/:id` |
| `GET` | `/api/v2/form/config` |
| `POST` | `/api/v1/algorithms/results` |
| `POST` | `/api/v1/casbin/user/device` |
| `POST` | `/api/v1/casbin/user/device_group` |
| `POST` | `/api/v1/device/batch/import` |
| `POST` | `/api/v1/device/disconnect` |
| `POST` | `/api/v1/device/model/custom/commands/` |
| `POST` | `/api/v1/device/preRegister` |
| `POST` | `/api/v1/forwarding/rule` |
| `POST` | `/api/v1/forwarding/script` |
| `POST` | `/api/v1/forwarding/script/test` |
| `POST` | `/api/v1/forwarding/source` |
| `POST` | `/api/v1/forwarding/target` |
| `POST` | `/api/v1/login/wechat` |
| `POST` | `/api/v1/notice/test` |
| `POST` | `/api/v1/notification/services/config/sms/test` |
| `POST` | `/api/v1/plugin/notification` |
| `POST` | `/api/v1/product` |
| `POST` | `/api/v1/vis/plugin/dashboard` |
| `POST` | `/api/v1/vis/plugin/share` |
| `POST` | `/api/v1/vis/plugin/up` |
| `POST` | `/broadcast` |
| `PUT` | `/api/v1/casbin/user/device` |
| `PUT` | `/api/v1/casbin/user/device_group` |
| `PUT` | `/api/v1/device/model/custom/commands/` |
| `PUT` | `/api/v1/forwarding/rule` |
| `PUT` | `/api/v1/forwarding/rule/status` |
| `PUT` | `/api/v1/forwarding/script` |
| `PUT` | `/api/v1/forwarding/source` |
| `PUT` | `/api/v1/forwarding/target` |
| `PUT` | `/api/v1/ota/package/` |
| `PUT` | `/api/v1/product` |
| `PUT` | `/api/v1/sys_function/:function_id` |
| `PUT` | `/api/v1/vis/plugin/dashboard` |

## 仅在当前 router

| 方法 | 当前源码路径 |
|---|---|
| `DELETE` | `/api/v1/dashboard-menu/:dashboardId` |
| `GET` | `/api/v1/alarm/info` |
| `GET` | `/api/v1/dashboard-menu/:dashboardId` |
| `GET` | `/api/v1/device/dashboard-templates` |
| `GET` | `/api/v1/device/dashboard-templates/:id/compatible-devices` |
| `GET` | `/api/v1/device/group/counts` |
| `GET` | `/api/v1/device/market/bundles` |
| `GET` | `/api/v1/device/market/bundles/:bundleKey` |
| `GET` | `/api/v1/device/market/bundles/:bundleKey/precheck` |
| `GET` | `/api/v1/device/market/bundles/install/:id` |
| `GET` | `/api/v1/device/market/bundles/installations` |
| `GET` | `/api/v1/device/model/attributes` |
| `GET` | `/api/v1/device/model/commands` |
| `GET` | `/api/v1/device/model/events` |
| `GET` | `/api/v1/device/online/status/ws` |
| `GET` | `/api/v1/device/online/status/ws/batch` |
| `GET` | `/api/v1/device/template/market/detail/:market_id` |
| `GET` | `/api/v1/device/template/market/list` |
| `GET` | `/api/v1/dict/protocol/service` |
| `GET` | `/api/v1/ota/download/files/upgradePackage/:path/:file` |
| `GET` | `/api/v1/telemetry/datas/current/keys/ws` |
| `GET` | `/api/v1/telemetry/datas/current/ws` |
| `GET` | `/api/v1/telemetry/datas/history` |
| `GET` | `/api/v1/telemetry/datas/simulation/init` |
| `GET` | `/api/v1/tenant/has-admin` |
| `GET` | `/api/v1/tenant/setup-state` |
| `GET` | `/api/v1/user/tenant/statistics` |
| `GET` | `/files/*filepath` |
| `GET` | `/metrics` |
| `GET` | `/swagger/*any` |
| `POST` | `/api/v1/device/dashboard-templates/:id/instances` |
| `POST` | `/api/v1/device/gateway-sub-register` |
| `POST` | `/api/v1/device/market/bundles/download` |
| `POST` | `/api/v1/device/market/bundles/install` |
| `POST` | `/api/v1/device/market/bundles/install/:id/compensate` |
| `POST` | `/api/v1/device/market/bundles/install/:id/retry` |
| `POST` | `/api/v1/device/market/bundles/publish-draft` |
| `POST` | `/api/v1/device/market/dashboard-bundles` |
| `POST` | `/api/v1/device/market/dashboard-bundles/analyze` |
| `POST` | `/api/v1/device/model/custom/commands` |
| `POST` | `/api/v1/device/template/market/install` |
| `POST` | `/api/v1/device/template/market/login` |
| `POST` | `/api/v1/device/template/market/publish` |
| `POST` | `/api/v1/device/template/market/refresh` |
| `POST` | `/api/v1/telemetry/datas/simulation/send` |
| `POST` | `/api/v1/tenant/market-register` |
| `POST` | `/api/v1/tenant/super-admin/init` |
| `PUT` | `/api/v1/dashboard-menu/:dashboardId` |
| `PUT` | `/api/v1/device/market/bundles/install/:id/bindings` |
| `PUT` | `/api/v1/device/model/attributes` |
| `PUT` | `/api/v1/device/model/commands` |
| `PUT` | `/api/v1/device/model/custom/commands` |
| `PUT` | `/api/v1/device/model/events` |
| `PUT` | `/api/v1/ota/package` |
| `PUT` | `/api/v1/sys_function/:id` |
| `PUT` | `/api/v1/user/address/:id` |
| `PUT` | `/api/v1/user/update` |
