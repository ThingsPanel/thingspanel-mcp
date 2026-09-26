"""Register explicit MCP tools for the checked-in source-derived API manifest."""
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

from .api_client import ThingsPanelClient
from .config import config

logger = logging.getLogger(__name__)


def load_api_manifest(path: Optional[Path] = None) -> Dict[str, Any]:
    manifest_path = path or Path(__file__).with_name("api_manifest.json")
    with manifest_path.open("r", encoding="utf-8") as manifest_file:
        data = json.load(manifest_file)
    if data.get("schema_version") != 1 or not isinstance(data.get("operations"), list):
        raise ValueError("API清单格式无效")
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
        server.add_tool(
            tool_fn,
            name=operation["tool_name"],
            title=operation.get("summary") or operation["tool_name"],
            description=description,
            structured_output=True,
        )
        registered += 1
    return registered


def _make_tool_handler(operation: Dict[str, Any], client: ThingsPanelClient):
    method = operation["method"].upper()
    path = operation["path"]
    service = operation["service"]
    name = operation["tool_name"]
    requires_confirmation = bool(operation.get("destructive"))
    required_path_params = set(operation.get("path_parameters", []))
    stream = operation.get("stream")

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
    ) -> Dict[str, Any]:
        """Call exactly the method/path captured by this generated MCP tool."""
        params = path_params or {}
        missing = sorted(required_path_params - set(params))
        if missing:
            return {"ok": False, "error": {"type": "missing_path_parameter", "names": missing}}
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
                    "body": body,
                    "file_path": file_path,
                },
            }
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
            )
        except KeyError as exc:
            return {"ok": False, "error": {"type": "configuration", "message": str(exc)}}
        except (TypeError, ValueError) as exc:
            return {"ok": False, "error": {"type": "invalid_request", "message": str(exc)}}
        except Exception as exc:  # Keep credentials and response bodies out of logs.
            logger.warning("MCP API tool %s failed (%s)", name, exc.__class__.__name__)
            return {"ok": False, "error": {"type": "request_failed", "message": "API调用失败"}}

    invoke_api.__name__ = name
    invoke_api.__doc__ = operation.get("summary") or f"调用 {method} {path}"
    return invoke_api
