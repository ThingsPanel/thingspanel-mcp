# src/thingspanel_mcp/api_client.py
import httpx
import logging
import json
import re
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from .config import config

logger = logging.getLogger(__name__)

class ThingsPanelClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, transport=None):
        self.api_key = api_key
        self.base_url = base_url or config.base_url
        self.transport = transport
        if not self.api_key and not config.is_configured():
            logger.warning("ThingsPanel/ThingsVis credentials not provided; protected API calls require authentication.")
    
    async def _request(self, method: str, endpoint: str, params=None, json_data=None) -> Dict[str, Any]:
        """发送HTTP请求到ThingsPanel API"""
        result = await self.request_api(
            "thingspanel", method, endpoint, query=params, body=json_data
        )
        if result.get("ok"):
            return result.get("data") or {}
        error = result.get("error")
        if isinstance(error, dict) and "code" in error:
            return error
        return {
            "code": result.get("status", 500),
            "message": error.get("message", "API请求失败") if isinstance(error, dict) else "API请求失败",
        }

    async def request_api(
        self,
        service: str,
        method: str,
        endpoint: str,
        path_params: Optional[Dict[str, Any]] = None,
        query: Optional[Dict[str, Any]] = None,
        body: Any = None,
        profile: str = "default",
        file_path: Optional[str] = None,
        upload_field: str = "file",
        timeout: float = 30.0,
        stream: Optional[str] = None,
        stream_messages: int = 5,
        stream_seconds: float = 5.0,
    ) -> Any:
        """Call one allow-listed ThingsPanel or ThingsVis API operation.

        Endpoint paths are canonical (for example `/api/v1/device/:id`). The
        configured API prefix lets local Vite proxy URLs and direct server URLs
        use the same manifest.
        """
        credentials = config.get_profile(profile)
        if service == "thingspanel":
            base_url = self.base_url
            api_prefix = config.api_prefix
            token = credentials.get("thingspanel_token")
            api_key = credentials.get("thingspanel_api_key") or (
                self.api_key if profile == "default" else None
            )
            internal_secret = None
        elif service == "thingsvis":
            base_url = config.thingsvis_base_url
            api_prefix = config.thingsvis_api_prefix
            token = credentials.get("thingsvis_token")
            api_key = credentials.get("thingsvis_open_api_key")
            internal_secret = credentials.get("thingsvis_internal_secret")
            if endpoint.startswith("/api/open/v1/dashboards"):
                token = None
                if not api_key:
                    raise KeyError(f"profile {profile} 缺少 ThingsVis Dashboard Open API Key")
            elif endpoint.startswith("/api/open/v1/apps"):
                api_key = None
                if not token:
                    raise KeyError(f"profile {profile} 缺少 ThingsVis 登录令牌")
        else:
            raise ValueError(f"不支持的API服务: {service}")

        if service == "thingsvis" and endpoint == "/api/v1/auth/sso":
            thingspanel_token = credentials.get("thingspanel_token")
            if not thingspanel_token:
                raise KeyError(f"profile {profile} 缺少 ThingsPanel JWT，ThingsVis SSO 无法验证身份")
            # Never allow the caller to choose a role, user, or a different platform token.
            body = {"platform": "thingspanel", "platformToken": thingspanel_token}

        if endpoint.startswith("/api/v1/"):
            endpoint = api_prefix.rstrip("/") + endpoint[len("/api/v1"):]
        params = path_params or {}

        def replace_path_parameter(match):
            key = match.group(1) or match.group(2)
            if key not in params:
                raise ValueError(f"缺少路径参数: {key}")
            from urllib.parse import quote
            return quote(str(params[key]), safe="")

        endpoint = re.sub(r":([A-Za-z0-9_]+)|\*([A-Za-z0-9_]+)", replace_path_parameter, endpoint)
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        headers = {"Accept": "application/json"}
        if service == "thingspanel":
            if token:
                headers["x-token"] = token
                headers["Authorization"] = f"Bearer {token}"
            elif api_key:
                headers["x-api-key"] = api_key
        else:
            if token:
                headers["Authorization"] = f"Bearer {token}"
            elif api_key:
                headers["x-api-key"] = api_key
            if internal_secret:
                headers["x-internal-token"] = internal_secret

        if stream == "sse":
            return await self._request_sse(url, headers, query, stream_messages, stream_seconds)
        if stream == "websocket":
            return await self._request_websocket(
                url, headers, query, body, token, api_key, stream_messages, stream_seconds
            )

        try:
            async with httpx.AsyncClient(transport=self.transport) as client:
                if file_path:
                    upload = Path(file_path)
                    if not upload.is_file():
                        raise ValueError("上传文件不存在或不是普通文件")
                    with upload.open("rb") as file_handle:
                        response = await client.request(
                            method, url, params=query, data=body, files={upload_field: file_handle},
                            headers=headers, timeout=timeout,
                        )
                else:
                    if body is not None:
                        headers["Content-Type"] = "application/json"
                    response = await client.request(
                        method, url, params=query, json=body, headers=headers, timeout=timeout,
                    )

            new_token = response.headers.get("New-Token") or response.headers.get("new-token")
            if service == "thingspanel" and new_token and token:
                config.profiles[profile]["thingspanel_token"] = new_token

            if response.status_code >= 400:
                try:
                    error_body = response.json()
                except ValueError:
                    error_body = {"message": response.text[:2000]}
                return {"ok": False, "status": response.status_code, "error": error_body}

            if not response.content:
                return {"ok": True, "status": response.status_code, "data": None}
            try:
                data = response.json()
            except ValueError:
                data = response.text
            if service == "thingspanel" and isinstance(data, dict) and data.get("code") is not None:
                try:
                    business_code = int(data["code"])
                except (TypeError, ValueError):
                    business_code = None
                if business_code is not None and business_code != 200:
                    error = {"code": data["code"]}
                    if data.get("message") is not None:
                        error["message"] = data["message"]
                    result = {"ok": False, "status": response.status_code, "error": error}
                    if "data" in data:
                        result["data"] = data["data"]
                    return result
            return {"ok": True, "status": response.status_code, "data": data}
        except (httpx.TimeoutException, httpx.RequestError) as exc:
            logger.warning("API request failed (%s) for %s %s", exc.__class__.__name__, method, endpoint)
            return {"ok": False, "error": {"type": exc.__class__.__name__, "message": "API请求失败或超时"}}

    async def _request_sse(self, url, headers, query, max_messages, max_seconds):
        """Read a bounded number of SSE events so an MCP call always returns."""
        events = []
        status = 200
        timeout = httpx.Timeout(connect=min(max_seconds, 10), read=max_seconds, write=max_seconds, pool=max_seconds)

        async def consume():
            nonlocal status
            async with httpx.AsyncClient(transport=self.transport, timeout=timeout) as client:
                async with client.stream("GET", url, params=query, headers=headers) as response:
                    status = response.status_code
                    if response.status_code >= 400:
                        return {"ok": False, "status": response.status_code,
                                "error": {"message": (await response.aread()).decode("utf-8", "replace")[:2000]}}
                    current = {}
                    async for line in response.aiter_lines():
                        if not line:
                            if current:
                                events.append(current)
                                current = {}
                                if len(events) >= max_messages:
                                    break
                            continue
                        if line.startswith(":"):
                            continue
                        field, _, value = line.partition(":")
                        current[field] = value.lstrip()
                    if current and len(events) < max_messages:
                        events.append(current)
            return {"ok": True, "status": status, "data": {"events": events, "bounded": True}}

        try:
            return await asyncio.wait_for(consume(), timeout=max_seconds)
        except asyncio.TimeoutError:
            return {"ok": True, "status": status, "data": {"events": events, "bounded": True, "timed_out": True}}
        except httpx.TimeoutException:
            return {"ok": True, "status": 200, "data": {"events": events, "bounded": True, "timed_out": True}}
        except httpx.RequestError as exc:
            logger.warning("SSE request failed (%s)", exc.__class__.__name__)
            return {"ok": False, "error": {"type": exc.__class__.__name__, "message": "SSE连接失败"}}

    async def _request_websocket(self, url, headers, query, body, token, api_key, max_messages, max_seconds):
        """Connect, send the backend's first-message auth payload, and read bounded results."""
        try:
            from websockets.asyncio.client import connect
        except ImportError:
            return {"ok": False, "error": {"type": "dependency", "message": "WebSocket支持需要安装 websockets"}}
        from urllib.parse import urlencode
        from websockets.exceptions import ConnectionClosed

        ws_url = url.replace("https://", "wss://", 1).replace("http://", "ws://", 1)
        if query:
            ws_url += ("&" if "?" in ws_url else "?") + urlencode(query, doseq=True)
        ws_headers = {key: value for key, value in headers.items() if key.lower() != "accept"}
        initial = dict(body) if isinstance(body, dict) else {}
        if token and "token" not in initial:
            initial["token"] = token
        if api_key and "x-api-key" not in initial:
            initial["x-api-key"] = api_key
        results = []
        try:
            async with connect(ws_url, additional_headers=ws_headers, open_timeout=min(max_seconds, 10)) as websocket:
                await websocket.send(json.dumps(initial))
                deadline = asyncio.get_running_loop().time() + max_seconds
                while len(results) < max_messages:
                    remaining = deadline - asyncio.get_running_loop().time()
                    if remaining <= 0:
                        break
                    try:
                        results.append(await asyncio.wait_for(websocket.recv(), timeout=remaining))
                    except asyncio.TimeoutError:
                        break
                    except ConnectionClosed:
                        break
            return {"ok": True, "status": 200, "data": {"messages": results, "bounded": True}}
        except Exception as exc:
            logger.warning("WebSocket request failed (%s)", exc.__class__.__name__)
            return {"ok": False, "error": {"type": exc.__class__.__name__, "message": "WebSocket连接失败"}}
    
    # 设备相关方法
    async def get_devices(self, page: int = 1, page_size: int = 10, search: str = None) -> Dict[str, Any]:
        """
        获取设备列表
        
        参数:
            page: 页码，默认1
            page_size: 每页数量，默认10
            search: 搜索关键字
        """
        params = {
            "page": page,
            "page_size": page_size
        }
        if search:
            params["search"] = search
        
        return await self._request("GET", "/api/v1/device", params=params)
    
    async def get_device_detail(self, device_id: str) -> Dict[str, Any]:
        """获取设备详情"""
        return await self._request("GET", f"/api/v1/device/detail/{device_id}")
    
    async def get_device_online_status(self, device_id: str) -> Dict[str, Any]:
        """获取设备在线状态"""
        return await self._request("GET", f"/api/v1/device/online/status/{device_id}")
    
    # 遥测数据相关方法
    async def get_current_telemetry(self, device_id: str) -> Dict[str, Any]:
        """获取设备当前遥测数据"""
        return await self._request("GET", f"/api/v1/telemetry/datas/current/{device_id}")
    
    async def get_telemetry_by_keys(self, device_id: str, keys: List[str]) -> Dict[str, Any]:
        """根据key获取遥测数据"""
        params = {
            "device_id": device_id,
            "keys": keys
        }
        return await self._request("GET", "/api/v1/telemetry/datas/current/keys", params=params)
    
    async def get_telemetry_statistics(
        self, 
        device_id: str, 
        key: str, 
        time_range: str = "last_1h",
        aggregate_window: str = "no_aggregate",
        aggregate_function: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取设备遥测数据统计"""
        params = {
            "device_id": device_id,
            "key": key,
            "time_range": time_range,
            "aggregate_window": aggregate_window
        }
        
        if aggregate_function and aggregate_window != "no_aggregate":
            params["aggregate_function"] = aggregate_function
            
        if time_range == "custom":
            if start_time:
                params["start_time"] = start_time
            if end_time:
                params["end_time"] = end_time
                
        return await self._request("GET", "/api/v1/telemetry/datas/statistic", params=params)
    
    async def publish_telemetry(self, device_id: str, value: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        """下发遥测数据"""
        # 确保值是正确的格式（JSON字符串）
        if isinstance(value, dict):
            value_str = json.dumps(value)
        else:
            value_str = value
        
        data = {
            "device_id": device_id,
            "value": value_str
        }
        return await self._request("POST", "/api/v1/telemetry/datas/pub", json_data=data)
    
    # 属性数据相关方法
    async def get_device_attributes(self, device_id: str) -> Dict[str, Any]:
        """获取设备属性"""
        return await self._request("GET", f"/api/v1/attribute/datas/{device_id}")
    
    # 命令相关方法
    async def get_command_logs(
        self, 
        device_id: str, 
        page: int = 1, 
        page_size: int = 10,
        status: Optional[str] = None,
        operation_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取命令下发记录"""
        params = {
            "device_id": device_id,
            "page": page,
            "page_size": page_size
        }
        
        if status:
            params["status"] = status
        if operation_type:
            params["operation_type"] = operation_type
            
        return await self._request("GET", "/api/v1/command/datas/set/logs", params=params)
    
    # 看板相关方法
    
    async def get_tenant_id(self) -> Dict[str, Any]:
        """获取租户ID"""
        return await self._request("GET", "/api/v1/user/tenant/id")
    
    async def get_tenant_devices_info(self) -> Dict[str, Any]:
        """获取租户下设备信息"""
        return await self._request("GET", "/api/v1/board/tenant/device/info")
    
    async def get_message_count(self) -> Dict[str, Any]:
        """获取租户大致消息数量"""
        return await self._request("GET", "/api/v1/telemetry/datas/msg/count")
    
    async def get_device_trend(self) -> Dict[str, Any]:
        """获取设备在线离线趋势"""
        return await self._request("GET", "/api/v1/board/trend")

    async def get_device_model_sources(self, device_template_id: str) -> Dict[str, Any]:
        """获取设备模板的数据源列表（遥测、属性等）"""
        params = {
            "id": device_template_id
        }
        return await self._request("GET", "/api/v1/device/model/source/at/list", params=params)

    async def publish_attributes(self, device_id: str, value: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        """设置设备属性"""
        # 确保值是正确的格式（JSON字符串）
        if isinstance(value, dict):
            value_str = json.dumps(value)
        else:
            value_str = value
        
        data = {
            "device_id": device_id,
            "value": value_str
        }
        return await self._request("POST", "/api/v1/attribute/datas/pub", json_data=data)

    async def publish_command(self, device_id: str, value: Union[Dict[str, Any], str], identifier: str) -> Dict[str, Any]:
        """下发设备命令"""
        # 确保值是正确的格式（JSON字符串）
        if isinstance(value, dict):
            value_str = json.dumps(value)
        else:
            value_str = value
        
        data = {
            "device_id": device_id,
            "value": value_str,
            "Identify": identifier
        }
        return await self._request("POST", "/api/v1/command/datas/pub", json_data=data)

    async def get_device_model_commands(self, device_template_id: str, page: int = 1, page_size: int = 100) -> Dict[str, Any]:
        """获取设备模板的命令详情"""
        params = {
            "page": page,
            "page_size": page_size,
            "device_template_id": device_template_id
        }
        return await self._request("GET", "/api/v1/device/model/commands", params=params)

    async def get_device_model_by_type(self, device_template_id: str, model_type: str, page: int = 1, page_size: int = 100) -> Dict[str, Any]:
        """获取设备模板的指定类型物模型信息"""
        if model_type not in ["telemetry", "attributes", "commands", "events"]:
            raise ValueError(f"不支持的物模型类型: {model_type}")
        
        params = {
            "page": page,
            "page_size": page_size,
            "device_template_id": device_template_id
        }
        return await self._request("GET", f"/api/v1/device/model/{model_type}", params=params)
