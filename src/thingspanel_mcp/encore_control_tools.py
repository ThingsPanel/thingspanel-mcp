"""Native device commands and receipts for metadata candidate d4e0540b.

No command is sent without an explicit confirmation and idempotency key.
The server validates identity, tenant, pinned model and command parameters.
"""
import json
import re
from typing import Any, Dict, Optional
from uuid import UUID

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .api_client import ThingsPanelClient
from .encore_result import EncoreToolResult

_KEY = re.compile(r"^[A-Za-z0-9._:-]{8,128}$")


def _uuid(value: str) -> bool:
    try:
        return isinstance(value, str) and len(value) == 36 and UUID(value).int != 0
    except (ValueError, AttributeError):
        return False


def register_encore_control_tools(server: FastMCP, client: Optional[ThingsPanelClient] = None) -> int:
    api = client or ThingsPanelClient()

    async def send_native_device_command(device_id: str, identifier: str, snapshot_id: str,
                                         parameters: Dict[str, Any], idempotency_key: str,
                                         confirmed: bool = False, timeout_seconds: int = 30,
                                         delivery_mode: str = "immediate", expires_at: Optional[str] = None,
                                         label: Optional[str] = None, profile: str = "default") -> EncoreToolResult:
        """Submit a native command for a pinned model snapshot (candidate d4e0540b required).

        Explicit confirmation is required; returned state is service evidence,
        not proof the physical device completed the command. On unknown outcome,
        query existing receipts and retry only with the same idempotency key.
        """
        if not confirmed:
            return EncoreToolResult(ok=False, confirmation_required=True,
                                    summary="请确认设备命令后再提交；受理不代表设备执行成功。",
                                    request_preview={"device_id": device_id, "identifier": identifier,
                                                     "snapshot_id": snapshot_id, "parameters": parameters,
                                                     "timeout_seconds": timeout_seconds, "delivery_mode": delivery_mode,
                                                     "expires_at": expires_at, "label": label})
        if not _uuid(device_id) or not _uuid(snapshot_id) or not identifier.strip():
            return EncoreToolResult(ok=False, summary="设备、快照或命令标识无效。", error={"type": "invalid_request"})
        if not _KEY.fullmatch(idempotency_key):
            return EncoreToolResult(ok=False, summary="需要 8–128 个合法字符的幂等键。", error={"type": "invalid_idempotency_key"})
        if isinstance(timeout_seconds, bool) or not 1 <= timeout_seconds <= 300 or delivery_mode not in ("immediate", "when_online"):
            return EncoreToolResult(ok=False, summary="超时或投递方式无效。", error={"type": "invalid_request"})
        if expires_at is not None and delivery_mode != "when_online":
            return EncoreToolResult(ok=False, summary="过期时间只适用于上线后投递。", error={"type": "invalid_request"})
        if label is not None and len(label) > 100:
            return EncoreToolResult(ok=False, summary="命令标签过长。", error={"type": "invalid_request"})
        try:
            json.dumps(parameters, allow_nan=False)
        except (TypeError, ValueError):
            return EncoreToolResult(ok=False, summary="命令参数不是有效 JSON 对象。", error={"type": "invalid_request"})
        body = {"identifier": identifier, "snapshotId": snapshot_id, "parameters": parameters,
                "timeoutSeconds": timeout_seconds, "deliveryMode": delivery_mode}
        if expires_at is not None: body["expiresAt"] = expires_at
        if label is not None: body["label"] = label
        try:
            result = await api.request_api(service="encore", method="POST",
                                           endpoint="/api/v2/devices/:deviceID/command-executions",
                                           path_params={"deviceID": device_id}, body=body, profile=profile,
                                           idempotency_key=idempotency_key, outcome_sensitive=True)
        except (KeyError, ValueError):
            return EncoreToolResult(ok=False, summary="Encore 地址、身份或请求参数无效。",
                                    error={"type": "configuration"})
        except Exception:
            return EncoreToolResult(ok=False, summary="命令请求未完成；请先查询回执并保留原幂等键。",
                                    error={"type": "outcome_unknown"})
        if not isinstance(result, dict) or not result.get("ok"):
            error = result.get("error", {}) if isinstance(result, dict) else {"type": "invalid_response"}
            return EncoreToolResult(ok=False, summary="命令未确认完成，请查看错误及回执。",
                                    status=result.get("status") if isinstance(result, dict) else None, error=error)
        data = result.get("data")
        # A successful HTTP status without an execution identity cannot be
        # tracked and must not be represented as confirmed acceptance.
        receipt = data.get("data") if isinstance(data, dict) else None
        if not isinstance(receipt, dict) or not _uuid(receipt.get("id")) or not isinstance(receipt.get("state"), str) or not receipt.get("state"):
            return EncoreToolResult(ok=False, summary="命令响应缺少回执，结果未知；请使用原幂等键核对。",
                                    status=result.get("status"), error={"type": "outcome_unknown"})
        return EncoreToolResult(ok=True, summary="命令提交已返回；设备执行结果以回执状态为准。",
                                status=result.get("status"), data=data)

    async def get_native_command_receipt(device_id: str, execution_id: str,
                                         profile: str = "default") -> EncoreToolResult:
        """Read the native command receipt without claiming a physical outcome."""
        if not _uuid(device_id) or not _uuid(execution_id):
            return EncoreToolResult(ok=False, summary="设备或回执标识无效。", error={"type": "invalid_request"})
        try:
            result = await api.request_api(service="encore", method="GET",
                                           endpoint="/api/v2/devices/:deviceID/command-executions/:executionID",
                                           path_params={"deviceID": device_id, "executionID": execution_id}, profile=profile)
        except Exception:
            return EncoreToolResult(ok=False, summary="回执查询未完成。", error={"type": "request_failed"})
        if not isinstance(result, dict) or not result.get("ok"):
            return EncoreToolResult(ok=False, summary="回执查询失败。", status=result.get("status") if isinstance(result, dict) else None,
                                    error=result.get("error", {}) if isinstance(result, dict) else {"type": "invalid_response"})
        return EncoreToolResult(ok=True, summary="已读取命令回执；请以返回的 state 为准。",
                                status=result.get("status"), data=result.get("data"))

    async def list_native_command_receipts(device_id: str, page: int = 1, page_size: int = 20,
                                           identifier: Optional[str] = None, profile: str = "default") -> EncoreToolResult:
        """List native command receipts to help reconcile an uncertain submission."""
        if not _uuid(device_id) or isinstance(page, bool) or isinstance(page_size, bool) or page < 1 or not 1 <= page_size <= 100:
            return EncoreToolResult(ok=False, summary="设备标识或分页参数无效。", error={"type": "invalid_request"})
        query: Dict[str, Any] = {"page": page, "pageSize": page_size}
        if identifier is not None:
            if not identifier.strip():
                return EncoreToolResult(ok=False, summary="命令标识无效。", error={"type": "invalid_request"})
            query["identifier"] = identifier
        try:
            result = await api.request_api(service="encore", method="GET",
                                           endpoint="/api/v2/devices/:deviceID/command-executions",
                                           path_params={"deviceID": device_id}, query=query, profile=profile)
        except Exception:
            return EncoreToolResult(ok=False, summary="回执列表查询未完成。", error={"type": "request_failed"})
        if not isinstance(result, dict) or not result.get("ok"):
            return EncoreToolResult(ok=False, summary="回执列表查询失败。", status=result.get("status") if isinstance(result, dict) else None,
                                    error=result.get("error", {}) if isinstance(result, dict) else {"type": "invalid_response"})
        return EncoreToolResult(ok=True, summary="已读取命令回执列表。", status=result.get("status"), data=result.get("data"))

    server.add_tool(send_native_device_command, structured_output=True,
                    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=True))
    for tool in (get_native_command_receipt, list_native_command_receipts):
        server.add_tool(tool, structured_output=True,
                        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True))
    return 3
