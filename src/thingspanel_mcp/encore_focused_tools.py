"""Read-only MCP tools for the actual Encore API.

The native device endpoints require Community metadata candidate d4e0540b (or
an equivalent deployed version). ThingModel endpoints exist on Community main
7f694779. These helpers never fall back to legacy paths or guess runtime state.
"""

from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .api_client import ThingsPanelClient
from .encore_result import EncoreToolResult


def register_encore_focused_tools(server: FastMCP, client: Optional[ThingsPanelClient] = None,
                                  include_native: bool = True) -> int:
    api = client or ThingsPanelClient()

    async def read(path: str, summary: str, *, path_params: Optional[Dict[str, Any]] = None,
                   query: Optional[Dict[str, Any]] = None, profile: str = "default") -> Dict[str, Any]:
        try:
            result = await api.request_api(service="encore", method="GET", endpoint=path,
                                           path_params=path_params, query=query, profile=profile)
        except (KeyError, ValueError) as exc:
            # Do not expose potentially sensitive configuration contents.
            return {"ok": False, "summary": "Encore 配置或请求参数无效。", "error": {"type": type(exc).__name__}}
        except Exception as exc:
            return {"ok": False, "summary": "Encore 请求未完成。", "error": {"type": type(exc).__name__}}
        if not isinstance(result, dict) or result.get("ok") is not True:
            error = result.get("error", {}) if isinstance(result, dict) else {"type": "invalid_response"}
            status = result.get("status") if isinstance(result, dict) else None
            return {"ok": False, "summary": "Encore 读取失败；404 也可能表示目标版本尚未部署。", "status": status, "error": error}
        return {"ok": True, "summary": summary, "status": result.get("status"), "data": result.get("data")}

    def pagination(page: int, page_size: int, maximum: int) -> Optional[Dict[str, Any]]:
        if not isinstance(page, int) or isinstance(page, bool) or page < 1:
            return None
        if not isinstance(page_size, int) or isinstance(page_size, bool) or not 1 <= page_size <= maximum:
            return None
        return {"page": page, "pageSize": page_size}

    def invalid_page() -> Dict[str, Any]:
        return {"ok": False, "summary": "分页参数无效。", "error": {"type": "invalid_pagination"}}

    async def encore_list_devices(page: int = 1, page_size: int = 20,
                                  search: Optional[str] = None, profile: str = "default") -> Dict[str, Any]:
        """查询原生设备；需要部署 Community 设备元数据候选 d4e0540b 或兼容版本。"""
        query = pagination(page, page_size, 100)
        if query is None: return invalid_page()
        if search is not None: query["search"] = search
        return await read("/api/v2/devices", "已读取原生设备列表。", query=query, profile=profile)

    async def encore_get_device(device_id: str, profile: str = "default") -> Dict[str, Any]:
        """读取原生设备详情；需要部署 Community 设备元数据候选。"""
        return await read("/api/v2/devices/:deviceID", "已读取原生设备详情。", path_params={"deviceID": device_id}, profile=profile)

    async def encore_get_device_runtime_state(device_id: str, profile: str = "default") -> Dict[str, Any]:
        """读取原生设备运行状态；保留服务端原值，不推断离线或在线。需设备元数据候选。"""
        return await read("/api/v2/devices/:deviceID/runtime-state", "已读取服务端运行状态。", path_params={"deviceID": device_id}, profile=profile)

    async def encore_list_device_readings(device_id: str, page: int = 1, page_size: int = 20,
                                          kind: str = "telemetry", identifier: Optional[str] = None,
                                          from_time: Optional[str] = None, to_time: Optional[str] = None,
                                          aggregation: str = "raw", window: Optional[str] = None,
                                          profile: str = "default") -> Dict[str, Any]:
        """读取当前遥测、属性或事件；遥测历史使用 RFC3339 起止时间及可选聚合窗口。需设备元数据候选及可用的运行时。"""
        query = pagination(page, page_size, 100)
        if query is None: return invalid_page()
        if kind not in ("telemetry", "attribute", "event"):
            return {"ok": False, "summary": "读数类型无效。", "error": {"type": "invalid_kind"}}
        query["kind"] = kind
        if identifier is not None: query["identifier"] = identifier
        historical = from_time is not None or to_time is not None or aggregation != "raw" or window is not None
        if historical:
            if kind != "telemetry" or not identifier or not from_time or not to_time:
                return {"ok": False, "summary": "遥测历史需要标识和起止时间。", "error": {"type": "invalid_history_query"}}
            query.update({"from": from_time, "to": to_time, "aggregation": aggregation})
            if window is not None: query["window"] = window
        elif kind in ("telemetry", "attribute"):
            query["latestOnly"] = "true"
        return await read("/api/v2/devices/:deviceID/readings", "已读取设备读数。", path_params={"deviceID": device_id}, query=query, profile=profile)

    async def encore_list_thing_models(page: int = 1, page_size: int = 20,
                                       query: Optional[str] = None, profile: str = "default") -> Dict[str, Any]:
        """分页读取 Community Encore 的物模型。"""
        params = pagination(page, page_size, 200)
        if params is None: return invalid_page()
        if query is not None: params["query"] = query
        return await read("/api/v2/thing-models", "已读取物模型列表。", query=params, profile=profile)

    async def encore_get_thing_model(model_id: str, profile: str = "default") -> Dict[str, Any]:
        """读取 Community Encore 物模型详情。"""
        return await read("/api/v2/thing-models/:modelID", "已读取物模型。", path_params={"modelID": model_id}, profile=profile)

    async def encore_list_thing_model_versions(model_id: str, page: int = 1, page_size: int = 20,
                                               profile: str = "default") -> Dict[str, Any]:
        """分页读取物模型已发布版本。"""
        query = pagination(page, page_size, 200)
        if query is None: return invalid_page()
        return await read("/api/v2/thing-models/:modelID/versions", "已读取物模型版本。", path_params={"modelID": model_id}, query=query, profile=profile)

    async def encore_get_thing_model_version(model_id: str, revision: int, profile: str = "default") -> Dict[str, Any]:
        """读取指定物模型已发布快照。"""
        if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
            return {"ok": False, "summary": "版本号无效。", "error": {"type": "invalid_revision"}}
        return await read("/api/v2/thing-models/:modelID/versions/:publishedRevision", "已读取物模型快照。", path_params={"modelID": model_id, "publishedRevision": revision}, profile=profile)

    async def encore_get_thing_model_resources(model_id: str, profile: str = "default") -> Dict[str, Any]:
        """读取物模型当前资源。"""
        return await read("/api/v2/thing-models/:modelID/resources", "已读取物模型资源。", path_params={"modelID": model_id}, profile=profile)

    tools = [encore_list_thing_models, encore_get_thing_model,
             encore_list_thing_model_versions, encore_get_thing_model_version,
             encore_get_thing_model_resources]
    if include_native:
        tools = [encore_list_devices, encore_get_device, encore_get_device_runtime_state,
                 encore_list_device_readings] + tools
    for tool in tools:
        tool.__annotations__["return"] = EncoreToolResult
        server.add_tool(tool, structured_output=True,
                        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True))
    return len(tools)
