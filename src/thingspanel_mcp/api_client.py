# src/thingspanel_mcp/api_client.py
import httpx
import logging
import json
from typing import Dict, Any, Optional, List, Union
from .config import config

logger = logging.getLogger(__name__)

class ThingsPanelClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or config.api_key
        self.base_url = base_url or config.base_url
        if not self.api_key:
            logger.warning("API key not provided. API calls will likely fail.")
    
    async def _request(self, method: str, endpoint: str, params=None, json_data=None) -> Dict[str, Any]:
        """发送HTTP请求到ThingsPanel API"""
        url = f"{self.base_url}{endpoint}"
        headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
    
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