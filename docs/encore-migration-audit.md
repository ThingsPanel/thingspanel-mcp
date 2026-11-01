# Encore API migration audit

Source: `/private/tmp/mcp-encore-audit-7f694779` (Encore declarations under `encore-api/`).
Compared with `src/thingspanel_mcp/encore_manifest.json`.

This is an inventory aid, not an exposure allow-list. Matches compare literal declaration paths only, including disabled entries; wildcard raw handlers and dedicated upload/download tools are not expanded. An unmatched path is not proof that an operation is unavailable. A public declaration may enforce authorization inside a raw handler. Verify source version, handler authorization, deployment routing and every method before enabling a tool.

Declared operations: **193**; manifest matches: **87**; unmatched: **106**.

## Counts

| Visibility | Operation class | Manifest match | Count |
|---|---|---:|---:|
| authenticated | read | no | 25 |
| authenticated | read | yes | 32 |
| authenticated | write_unconfirmed | no | 49 |
| authenticated | write_unconfirmed | yes | 41 |
| public_declaration | read | no | 15 |
| public_declaration | read | yes | 9 |
| public_declaration | write_unconfirmed | no | 17 |
| public_declaration | write_unconfirmed | yes | 5 |

## Per-operation inventory

| Method | Path | Visibility | Safety | Manifest | Migration disposition | Source |
|---|---|---|---|---|---|---|
| DELETE | `/api/custom-command-controls/:id` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/custom_control_service.go` |
| DELETE | `/api/device-templates/:id` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| DELETE | `/api/devices/:id` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| DELETE | `/api/products/:id` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| DELETE | `/api/thing-model-items/:id` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| DELETE | `/api/thing-models/:id` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| DELETE | `/api/thing-models/:tmId/items/:id` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| DELETE | `/v1/bindings/:id` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/binding_service.go` |
| DELETE | `/v1/connections/:id` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/northbound/connections.go` |
| DELETE | `/v1/pipelines/:id` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/northbound/pipelines.go` |
| DELETE | `/v1/rules/:id` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/reference_service.go` |
| DELETE | `/v1/schedules/:id` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/service.go` |
| GET | `/api/custom-command-controls` | authenticated | read | no | review_required | `encore-api/devicemetadata/custom_control_service.go` |
| GET | `/api/device-templates` | authenticated | read | no | review_required | `encore-api/devicemetadata/service.go` |
| GET | `/api/device-templates/:id` | authenticated | read | no | review_required | `encore-api/devicemetadata/service.go` |
| GET | `/api/devices` | authenticated | read | no | review_required | `encore-api/devicemetadata/service.go` |
| GET | `/api/devices/:id` | authenticated | read | no | review_required | `encore-api/devicemetadata/service.go` |
| GET | `/api/devices/:id/latest` | authenticated | read | no | review_required | `encore-api/devicemetadata/service.go` |
| GET | `/api/meta-item-keys` | authenticated | read | no | review_required | `encore-api/devicemetadata/service.go` |
| GET | `/api/migrate/history` | authenticated | read | no | review_required | `encore-api/devicemetadata/migration_service.go` |
| GET | `/api/product-keys/:productKey` | authenticated | read | no | review_required | `encore-api/devicemetadata/service.go` |
| GET | `/api/products` | authenticated | read | no | review_required | `encore-api/devicemetadata/service.go` |
| GET | `/api/products/:id` | authenticated | read | no | review_required | `encore-api/devicemetadata/service.go` |
| GET | `/api/templates/:templateID/products` | authenticated | read | no | review_required | `encore-api/devicemetadata/service.go` |
| GET | `/api/thing-models` | authenticated | read | no | review_required | `encore-api/devicemetadata/service.go` |
| GET | `/api/thing-models/:id` | authenticated | read | no | review_required | `encore-api/devicemetadata/service.go` |
| GET | `/api/thing-models/:id/diff` | authenticated | read | no | review_required | `encore-api/devicemetadata/service.go` |
| GET | `/api/thing-models/:id/versions` | authenticated | read | no | review_required | `encore-api/devicemetadata/service.go` |
| GET | `/api/thing-models/:id/versions/:version` | authenticated | read | no | review_required | `encore-api/devicemetadata/service.go` |
| GET | `/api/thing-models/:thingModelID/device-templates` | authenticated | read | no | review_required | `encore-api/devicemetadata/service.go` |
| GET | `/api/thing-models/:tmId/items` | authenticated | read | no | review_required | `encore-api/devicemetadata/service.go` |
| GET | `/api/thing-models/:tmId/items/:id` | authenticated | read | no | review_required | `encore-api/devicemetadata/service.go` |
| GET | `/api/v2/thing-models` | authenticated | read | match | review_required | `encore-api/thingmodel/service.go` |
| GET | `/api/v2/thing-models/:modelID` | authenticated | read | match | review_required | `encore-api/thingmodel/service.go` |
| GET | `/api/v2/thing-models/:modelID/resources` | authenticated | read | match | review_required | `encore-api/thingmodel/service.go` |
| GET | `/api/v2/thing-models/:modelID/versions` | authenticated | read | match | review_required | `encore-api/thingmodel/service.go` |
| GET | `/api/v2/thing-models/:modelID/versions/:publishedRevision` | authenticated | read | match | review_required | `encore-api/thingmodel/service.go` |
| GET | `/v1/alarm-reconcile` | authenticated | read | match | review_required | `encore-api/automation/service.go` |
| GET | `/v1/alarms` | authenticated | read | match | review_required | `encore-api/automation/service.go` |
| GET | `/v1/alarms/:id` | authenticated | read | match | review_required | `encore-api/automation/service.go` |
| GET | `/v1/alarms/:id/transitions` | authenticated | read | match | review_required | `encore-api/automation/service.go` |
| GET | `/v1/backlog` | authenticated | read | no | review_required | `encore-api/automation/service.go` |
| GET | `/v1/blueprints` | authenticated | read | match | review_required | `encore-api/automation/blueprint_service.go` |
| GET | `/v1/bundles/imports` | authenticated | read | match | review_required | `encore-api/automation/bundle_service.go` |
| GET | `/v1/bundles/imports/:id` | authenticated | read | match | review_required | `encore-api/automation/bundle_service.go` |
| GET | `/v1/connections` | authenticated | read | match | review_required | `encore-api/northbound/connections.go` |
| GET | `/v1/connections/:id` | authenticated | read | match | review_required | `encore-api/northbound/connections.go` |
| GET | `/v1/connectors` | authenticated | read | match | review_required | `encore-api/northbound/catalog.go` |
| GET | `/v1/deliveries` | authenticated | read | match | review_required | `encore-api/northbound/deliveries.go` |
| GET | `/v1/device-automation/:deviceId` | authenticated | read | match | review_required | `encore-api/automation/binding_service.go` |
| GET | `/v1/device-configs/:id/bindings` | authenticated | read | match | review_required | `encore-api/automation/binding_service.go` |
| GET | `/v1/events` | authenticated | read | match | review_required | `encore-api/automation/service.go` |
| GET | `/v1/executors` | authenticated | read | no | review_required | `encore-api/automation/executor_service.go` |
| GET | `/v1/executors/:id/messages` | authenticated | read | no | review_required | `encore-api/automation/executor_service.go` |
| GET | `/v1/legacy-refs/:legacyId` | authenticated | read | no | review_required | `encore-api/automation/service.go` |
| GET | `/v1/migrations/:id` | authenticated | read | no | review_required | `encore-api/automation/migration_service.go` |
| GET | `/v1/overview` | authenticated | read | match | review_required | `encore-api/northbound/overview.go` |
| GET | `/v1/pipelines` | authenticated | read | match | review_required | `encore-api/northbound/pipelines.go` |
| GET | `/v1/pipelines/:id` | authenticated | read | match | review_required | `encore-api/northbound/pipelines.go` |
| GET | `/v1/rules` | authenticated | read | match | review_required | `encore-api/automation/service.go` |
| GET | `/v1/rules/:id` | authenticated | read | match | review_required | `encore-api/automation/service.go` |
| GET | `/v1/rules/:id/bindings` | authenticated | read | match | review_required | `encore-api/automation/binding_service.go` |
| GET | `/v1/rules/:id/blueprint` | authenticated | read | match | review_required | `encore-api/automation/blueprint_service.go` |
| GET | `/v1/rules/:id/explain` | authenticated | read | match | review_required | `encore-api/automation/service.go` |
| GET | `/v1/rules/:id/runs` | authenticated | read | match | review_required | `encore-api/automation/service.go` |
| GET | `/v1/runs/:runId` | authenticated | read | match | review_required | `encore-api/automation/service.go` |
| GET | `/v1/schedules` | authenticated | read | match | review_required | `encore-api/automation/service.go` |
| GET | `/v1/schedules/:id` | authenticated | read | match | review_required | `encore-api/automation/service.go` |
| GET | `/v1/schedules/:id/fires` | authenticated | read | match | review_required | `encore-api/automation/service.go` |
| POST | `/api/custom-command-controls` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/custom_control_service.go` |
| POST | `/api/device-templates` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| POST | `/api/device-templates/:id/archive` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| POST | `/api/device-templates/:id/bind-thing-model` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| POST | `/api/device-templates/:id/derive-draft` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| POST | `/api/device-templates/:id/publish` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| POST | `/api/devices` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| POST | `/api/devices/:id/actuate` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| POST | `/api/migrate/all-legacy-templates` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/migration_service.go` |
| POST | `/api/migrate/device-topic/:deviceID` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/migration_service.go` |
| POST | `/api/migrate/from-legacy-template/:legacyTemplateID` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/migration_service.go` |
| POST | `/api/migrate/rollback/:migrationID` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/migration_service.go` |
| POST | `/api/products` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| POST | `/api/thing-models` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| POST | `/api/thing-models/:id/archive` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| POST | `/api/thing-models/:id/derive-draft` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| POST | `/api/thing-models/:id/publish` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| POST | `/api/thing-models/:id/rollback` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| POST | `/api/thing-models/:tmId/items` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| POST | `/api/thing-models/:tmId/items/batch` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| POST | `/api/v2/thing-model-commands/create` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/thingmodel/service.go` |
| POST | `/api/v2/thing-model-commands/publish` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/thingmodel/service.go` |
| POST | `/api/v2/thing-model-commands/update` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/thingmodel/service.go` |
| POST | `/api/v2/thing-model-commands/update-resources` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/thingmodel/service.go` |
| POST | `/api/validate/device-template` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| POST | `/api/validate/thing-model` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| POST | `/api/validate/thing-model-item` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| POST | `/v1/alarm-policies/:id/events` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/automation/service.go` |
| POST | `/v1/alarms/:id/ack` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/service.go` |
| POST | `/v1/binding-reconcile` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/reference_service.go` |
| POST | `/v1/blueprint-preview` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/blueprint_service.go` |
| POST | `/v1/blueprints/:key/instantiate` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/blueprint_service.go` |
| POST | `/v1/bundles/export` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/bundle_service.go` |
| POST | `/v1/bundles/import` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/bundle_service.go` |
| POST | `/v1/bundles/preview` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/bundle_service.go` |
| POST | `/v1/connections` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/northbound/connections.go` |
| POST | `/v1/connections/:id/test` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/northbound/connections.go` |
| POST | `/v1/deliveries/:id/replay` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/northbound/deliveries.go` |
| POST | `/v1/executors` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/automation/executor_service.go` |
| POST | `/v1/executors/:id/heartbeat` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/automation/executor_service.go` |
| POST | `/v1/executors/:id/intents` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/automation/executor_service.go` |
| POST | `/v1/executors/:id/verdicts` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/automation/executor_service.go` |
| POST | `/v1/ingress/events` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/automation/service.go` |
| POST | `/v1/ingress/uplink` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/automation/service.go` |
| POST | `/v1/legacy/scene-plan` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/automation/service.go` |
| POST | `/v1/migrations` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/automation/migration_service.go` |
| POST | `/v1/migrations/:id/apply` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/automation/migration_service.go` |
| POST | `/v1/migrations/:id/rollback` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/automation/migration_service.go` |
| POST | `/v1/migrations/:id/verify` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/automation/migration_service.go` |
| POST | `/v1/pipelines` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/northbound/pipelines.go` |
| POST | `/v1/pipelines/:id/activate` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/northbound/pipelines.go` |
| POST | `/v1/pipelines/:id/disable` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/northbound/pipelines.go` |
| POST | `/v1/pipelines/:id/pause` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/northbound/pipelines.go` |
| POST | `/v1/pipelines/:id/preview` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/northbound/pipelines.go` |
| POST | `/v1/pipelines/:id/test-send` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/northbound/pipelines.go` |
| POST | `/v1/rule-validation` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/service.go` |
| POST | `/v1/rules` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/service.go` |
| POST | `/v1/rules/:id/bindings` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/binding_service.go` |
| POST | `/v1/rules/:id/blueprint/upgrade` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/blueprint_service.go` |
| POST | `/v1/rules/:id/change-preview` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/change_preview.go` |
| POST | `/v1/rules/:id/enabled` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/service.go` |
| POST | `/v1/rules/:id/revision-check` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/reference_service.go` |
| POST | `/v1/rules/:id/run` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/service.go` |
| POST | `/v1/rules/:id/simulate` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/service.go` |
| POST | `/v1/schedule-preview` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/service.go` |
| POST | `/v1/schedules` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/service.go` |
| POST | `/v1/schedules/:id/enabled` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/service.go` |
| PUT | `/api/custom-command-controls` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/custom_control_service.go` |
| PUT | `/api/device-templates/:id` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| PUT | `/api/devices/:id` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| PUT | `/api/products/:id` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| PUT | `/api/thing-model-items/:id` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| PUT | `/api/thing-models/:id` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| PUT | `/api/thing-models/:tmId/items/:id` | authenticated | write_unconfirmed | no | review_only_unconfirmed | `encore-api/devicemetadata/service.go` |
| PUT | `/v1/connections/:id` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/northbound/connections.go` |
| PUT | `/v1/pipelines/:id` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/northbound/pipelines.go` |
| PUT | `/v1/rules/:id` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/service.go` |
| PUT | `/v1/schedules/:id` | authenticated | write_unconfirmed | match | review_only_unconfirmed | `encore-api/automation/service.go` |
| GET | `/api/device-metadata/healthz` | public_declaration | read | no | review_required | `encore-api/devicemetadata/service.go` |
| GET | `/api/dictionaries` | public_declaration | read | no | review_required | `encore-api/devicemetadata/service.go` |
| GET | `/api/public/meta-item-keys` | public_declaration | read | no | review_required | `encore-api/devicemetadata/service.go` |
| GET | `/api/v1/notification-source/group-snapshots/:id` | public_declaration | read | no | review_required | `encore-api/l3-core/notification/api_v2.go` |
| GET | `/api/v1/tenant/has-admin` | public_declaration | read | no | review_required | `encore-api/l1-access/authn/endpoints.go` |
| GET | `/api/v1/tenant/setup-state` | public_declaration | read | no | review_required | `encore-api/l1-access/authn/endpoints.go` |
| GET | `/api/v1/user/detail` | public_declaration | read | no | review_required | `encore-api/l1-access/authn/endpoints.go` |
| GET | `/api/v1/user/logout` | public_declaration | read | no | review_required | `encore-api/l1-access/authn/endpoints.go` |
| GET | `/api/v1/user/refresh` | public_declaration | read | no | review_required | `encore-api/l1-access/authn/endpoints.go` |
| GET | `/api/v2/notification-deliveries` | public_declaration | read | match | review_required | `encore-api/l3-core/notification/api_v2.go` |
| GET | `/api/v2/notification-deliveries/:id` | public_declaration | read | match | review_required | `encore-api/l3-core/notification/api_v2.go` |
| GET | `/api/v2/notification-groups` | public_declaration | read | match | review_required | `encore-api/l3-core/notification/api_v2.go` |
| GET | `/api/v2/notification-groups/:id` | public_declaration | read | match | review_required | `encore-api/l3-core/notification/api_v2.go` |
| GET | `/api/v2/notification-instances` | public_declaration | read | match | review_required | `encore-api/l3-core/notification/api_v2.go` |
| GET | `/api/v2/notification-instances/*path` | public_declaration | read | no | review_required | `encore-api/l3-core/notification/api_v2.go` |
| GET | `/api/v2/notification-plugin-grants` | public_declaration | read | no | review_required | `encore-api/l3-core/notification/api_v2.go` |
| GET | `/api/v2/notification-plugins` | public_declaration | read | match | review_required | `encore-api/l3-core/notification/api_v2.go` |
| GET | `/api/v2/notification-plugins/:id` | public_declaration | read | match | review_required | `encore-api/l3-core/notification/api_v2.go` |
| GET | `/api/v2/notifications` | public_declaration | read | match | review_required | `encore-api/l3-core/notification/api_v2.go` |
| GET | `/api/v2/notifications/:id` | public_declaration | read | match | review_required | `encore-api/l3-core/notification/api_v2.go` |
| GET | `/api/v2/platform/notification-tenants/*path` | public_declaration | read | no | review_required | `encore-api/l3-core/notification/api_v2.go` |
| GET | `/v1/health` | public_declaration | read | no | review_required | `encore-api/automation/service.go` |
| GET | `/v1/notifications/history` | public_declaration | read | no | review_required | `encore-api/l3-core/notification/service.go` |
| GET | `/v1/subscriptions` | public_declaration | read | no | review_required | `encore-api/northbound/subscriptions.go` |
| POST | `/api/v1/login` | public_declaration | write_unconfirmed | no | review_only_unconfirmed | `encore-api/l1-access/authn/endpoints.go` |
| POST | `/api/v1/notification-instances/:instance_id/receipts` | public_declaration | write_unconfirmed | no | review_only_unconfirmed | `encore-api/l3-core/notification/api_v2.go` |
| POST | `/api/v1/tenant/email/register` | public_declaration | write_unconfirmed | no | review_only_unconfirmed | `encore-api/l1-access/authn/endpoints.go` |
| POST | `/api/v1/tenant/market-register` | public_declaration | write_unconfirmed | no | review_only_unconfirmed | `encore-api/l1-access/authn/endpoints.go` |
| POST | `/api/v1/tenant/super-admin/init` | public_declaration | write_unconfirmed | no | review_only_unconfirmed | `encore-api/l1-access/authn/endpoints.go` |
| POST | `/api/v1/user/transform` | public_declaration | write_unconfirmed | no | review_only_unconfirmed | `encore-api/l1-access/authn/endpoints.go` |
| POST | `/api/v2/notification-group-projections` | public_declaration | write_unconfirmed | no | review_only_unconfirmed | `encore-api/l3-core/notification/api_v2.go` |
| POST | `/api/v2/notification-groups` | public_declaration | write_unconfirmed | match | review_only_unconfirmed | `encore-api/l3-core/notification/api_v2.go` |
| POST | `/api/v2/notification-ingress/events` | public_declaration | write_unconfirmed | no | review_only_unconfirmed | `encore-api/l3-core/notification/api_v2.go` |
| POST | `/api/v2/notification-instances` | public_declaration | write_unconfirmed | no | review_only_unconfirmed | `encore-api/l3-core/notification/api_v2.go` |
| POST | `/api/v2/notification-instances/*path` | public_declaration | write_unconfirmed | no | review_only_unconfirmed | `encore-api/l3-core/notification/api_v2.go` |
| POST | `/api/v2/notification-plugins` | public_declaration | write_unconfirmed | match | review_only_unconfirmed | `encore-api/l3-core/notification/api_v2.go` |
| POST | `/api/v2/notifications` | public_declaration | write_unconfirmed | match | review_only_unconfirmed | `encore-api/l3-core/notification/api_v2.go` |
| POST | `/api/v2/platform/notification-tenants/*path` | public_declaration | write_unconfirmed | no | review_only_unconfirmed | `encore-api/l3-core/notification/api_v2.go` |
| POST | `/internal/automation/tick` | public_declaration | write_unconfirmed | no | review_only_unconfirmed | `encore-api/automation/owner_tick.go` |
| POST | `/internal/automation/uplink` | public_declaration | write_unconfirmed | no | review_only_unconfirmed | `encore-api/automation/owner_uplink.go` |
| POST | `/v1/inbox/events` | public_declaration | write_unconfirmed | no | review_only_unconfirmed | `encore-api/northbound/inbox.go` |
| PUT | `/api/v2/notification-groups/:id` | public_declaration | write_unconfirmed | match | review_only_unconfirmed | `encore-api/l3-core/notification/api_v2.go` |
| PUT | `/api/v2/notification-instances/*path` | public_declaration | write_unconfirmed | no | review_only_unconfirmed | `encore-api/l3-core/notification/api_v2.go` |
| PUT | `/api/v2/notification-plugin-grants` | public_declaration | write_unconfirmed | no | review_only_unconfirmed | `encore-api/l3-core/notification/api_v2.go` |
| PUT | `/api/v2/notification-plugins/:id` | public_declaration | write_unconfirmed | match | review_only_unconfirmed | `encore-api/l3-core/notification/api_v2.go` |
| PUT | `/api/v2/platform/notification-tenants/*path` | public_declaration | write_unconfirmed | no | review_only_unconfirmed | `encore-api/l3-core/notification/api_v2.go` |
