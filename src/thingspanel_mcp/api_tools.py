"""Register explicit MCP tools for the checked-in source-derived API manifest."""
import json
import logging
import re
import os
from pathlib import Path
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .api_client import ThingsPanelClient
from .config import config
from .encore_result import EncoreToolResult

logger = logging.getLogger(__name__)


def load_api_manifest(path: Optional[Path] = None) -> Dict[str, Any]:
    manifest_path = path or Path(__file__).with_name("api_manifest.json")
    with manifest_path.open("r", encoding="utf-8") as manifest_file:
        data = json.load(manifest_file)
    if data.get("schema_version") != 1 or not isinstance(data.get("operations"), list):
        raise ValueError("API清单格式无效")
    return data


def load_encore_manifest() -> Dict[str, Any]:
    data = load_api_manifest(Path(__file__).with_name("encore_manifest.json"))
    enable_native = os.environ.get("THINGSPANEL_ENABLE_NATIVE_METADATA") == "1"
    enable_northbound = os.environ.get("THINGSPANEL_ENABLE_NORTHBOUND") == "1"
    data["operations"] = [dict(op, enabled=True) if ((enable_native and op.get("availability") == "metadata_candidate") or
                                                       (enable_northbound and op.get("availability") == "community_optional")) else op
                          for op in data["operations"]]
    return data


def register_api_tools(server: FastMCP, client: Optional[ThingsPanelClient] = None,
                       manifest: Optional[Dict[str, Any]] = None) -> int:
    """Register enabled operations as individually named, allow-listed MCP tools."""
    api_client = client or ThingsPanelClient()
    api_manifest = manifest or load_api_manifest()
    registered = 0

    for operation in api_manifest["operations"]:
        if not operation.get("enabled", False):
            continue
        tool_fn = _make_tool_handler(operation, api_client)
        description = (
            f"{operation.get('summary') or 'ThingsPanel API'}。"
            f"接口：{operation['method']} {operation['path']}。"
            f"身份策略：{operation.get('security', '服务端鉴权')}。"
            "路径变量放在 path_params，查询参数放在 query，JSON 请求体放在 body。"
        )
        if operation.get("stream"):
            description += "流接口最多读取 20 条消息或 30 秒；WebSocket 首条鉴权/订阅消息放在 body。"
        if operation.get("sensitive_response"):
            description += "响应可能含敏感信息，只向有权用户展示，不应记录或缓存。"
        server.add_tool(
            tool_fn,
            name=operation["tool_name"],
            title=operation.get("summary") or operation["tool_name"],
            description=description,
            structured_output=True,
            annotations=ToolAnnotations(
                readOnlyHint=not operation.get("write", operation.get("destructive", False)),
                destructiveHint=bool(operation.get("destructive")),
                idempotentHint=not operation.get("write", operation.get("destructive", False)) or bool(operation.get("requires_idempotency")),
                openWorldHint=True,
            ),
        )
        registered += 1
    return registered


def _make_tool_handler(operation: Dict[str, Any], client: ThingsPanelClient):
    method = operation["method"].upper()
    path = operation["path"]
    service = operation["service"]
    name = operation["tool_name"]
    requires_confirmation = bool(operation.get("destructive") or (service == "encore" and operation.get("write")))
    required_path_params = set(operation.get("path_parameters", []))
    stream = operation.get("stream")
    requires_idempotency = bool(operation.get("requires_idempotency"))
    idempotency_location = operation.get("idempotency_location", "header")
    requires_if_match = bool(operation.get("requires_if_match"))

    async def invoke_api(
        path_params: Optional[Dict[str, Any]] = None,
        query: Optional[Dict[str, Any]] = None,
        body: Any = None,
        file_path: Optional[str] = None,
        upload_field: str = "file",
        profile: str = "default",
        confirmed: bool = False,
        stream_messages: int = 5,
        stream_seconds: float = 5.0,
        idempotency_key: Optional[str] = None,
        if_match: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Call exactly the method/path captured by this generated MCP tool."""
        params = path_params or {}
        missing = sorted(required_path_params - set(params))
        if missing:
            return {"ok": False, "error": {"type": "missing_path_parameter", "names": missing}}
        if service == "encore" and any(str(value) in (".", "..") or any(ch in str(value) for ch in "/?#%") for value in params.values()):
            return {"ok": False, "error": {"type": "invalid_request", "message": "路径参数不能包含路径或查询分隔符"}}
        if service == "encore" and set(query or {}) - set(operation.get("query_parameters", [])):
            return {"ok": False, "error": {"type": "invalid_request", "message": "包含接口不支持的查询参数"}}
        if requires_confirmation and not confirmed:
            return {
                "ok": False,
                "confirmation_required": True,
                "request_preview": {
                    "service": service,
                    "method": method,
                    "path": path,
                    "path_params": params,
                    "query": query or {},
                    **({"body_provided": body is not None, "file_provided": bool(file_path)} if service == "encore" else {"body": body, "file_path": file_path}),
                },
            }
        if requires_idempotency and not (idempotency_key and idempotency_key.strip()):
            return {"ok": False, "error": {"type": "missing_idempotency_key", "message": "该操作需要 Idempotency-Key"}}
        if service == "encore" and idempotency_key and not requires_idempotency:
            return {"ok": False, "error": {"type": "unsupported_idempotency_key", "message": "该接口没有已确认的幂等键契约"}}
        if service == "encore" and operation.get("body_required") and not isinstance(body, dict):
            return {"ok": False, "error": {"type": "invalid_request", "message": "该操作需要 JSON 对象请求体"}}
        if service == "encore" and idempotency_key and not re.fullmatch(r"[A-Za-z0-9._:-]{8,128}", idempotency_key):
            return {"ok": False, "error": {"type": "invalid_idempotency_key", "message": "幂等键须为 8–128 个允许的 ASCII 字符"}}
        if requires_if_match and (not if_match or not re.fullmatch(r'"[^"\r\n]*"', if_match)):
            return {"ok": False, "error": {"type": "missing_if_match", "message": "需要服务端原样返回的强 ETag"}}
        if requires_idempotency and idempotency_location == "body":
            if not isinstance(body, dict):
                return {"ok": False, "error": {"type": "invalid_request", "message": "该操作需要 JSON 对象请求体"}}
            if body.get("request_id") not in (None, idempotency_key):
                return {"ok": False, "error": {"type": "invalid_request", "message": "request_id 与幂等键不一致"}}
            body = {**body, "request_id": idempotency_key}
        if stream_messages < 1 or stream_messages > 20 or stream_seconds < 1 or stream_seconds > 30:
            return {"ok": False, "error": {"type": "invalid_request", "message": "流读取限制为 1-20 条消息、1-30 秒"}}
        try:
            return await client.request_api(
                service=service,
                method=method,
                endpoint=path,
                path_params=params,
                query=query,
                body=body,
                profile=profile,
                file_path=file_path,
                upload_field=upload_field,
                stream=stream,
                stream_messages=stream_messages,
                stream_seconds=stream_seconds,
                **({"idempotency_key": idempotency_key} if idempotency_key and idempotency_location == "header" else {}),
                **({"if_match": if_match} if if_match else {}),
                **({"outcome_sensitive": True} if service == "encore" and operation.get("write") else {}),
            )
        except KeyError as exc:
            return {"ok": False, "error": {"type": "configuration", "message": str(exc)}}
        except (TypeError, ValueError) as exc:
            return {"ok": False, "error": {"type": "invalid_request", "message": str(exc)}}
        except Exception as exc:  # Keep credentials and response bodies out of logs.
            logger.warning("MCP API tool %s failed (%s)", name, exc.__class__.__name__)
            return {"ok": False, "error": {"type": "request_failed", "message": "API调用失败"}}

    invoke_api.__name__ = name
    if service == "encore":
        invoke_api.__annotations__["return"] = EncoreToolResult
    invoke_api.__doc__ = operation.get("summary") or f"调用 {method} {path}"
    return invoke_api
