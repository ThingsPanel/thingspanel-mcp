# src/thingspanel_mcp/server.py
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from mcp.server.fastmcp import FastMCP, Context
from .config import config
from .tools import device_tools, telemetry_tools, dashboard_tools, control_tools
from .prompts import common_prompts
from .api_tools import register_api_tools

logger = logging.getLogger(__name__)

class ThingsPanelServer:
    """ThingsPanel MCP 服务器"""
    
    def __init__(self, server_name: str = "ThingsPanel"):
        """初始化ThingsPanel MCP服务器"""
        self.server = FastMCP(server_name)
        self._setup_tools()
        self._setup_prompts()
        
    def _setup_tools(self):
        """设置服务器工具"""
        # 设备相关工具
        self.server.tool(structured_output=True)(device_tools.list_devices)
        self.server.tool(structured_output=True)(device_tools.get_device_detail)
        self.server.tool(structured_output=True)(device_tools.check_device_status)
        
        # 遥测数据相关工具
        self.server.tool(structured_output=True)(telemetry_tools.get_device_telemetry)
        self.server.tool(structured_output=True)(telemetry_tools.get_telemetry_by_key)
        self.server.tool(structured_output=True)(telemetry_tools.get_telemetry_history)
        
        # 看板相关工具
        self.server.tool(structured_output=True)(dashboard_tools.get_tenant_summary)
        self.server.tool(structured_output=True)(dashboard_tools.get_device_trend_report)
        
        # 设备控制相关工具
        self.server.tool(structured_output=True)(control_tools.get_device_model_info)
        self.server.tool(structured_output=True)(control_tools.control_device_telemetry)
        self.server.tool(structured_output=True)(control_tools.set_device_attributes)
        self.server.tool(structured_output=True)(control_tools.send_device_command)
        self.server.tool(structured_output=True)(control_tools.get_device_command_status)
        self.server.tool(structured_output=True)(control_tools.control_device_with_model_check)

        # 为源码清单中的每个 API 操作注册独立的 allow-listed MCP tool。
        self.api_tool_count = register_api_tools(self.server)
        
    def _setup_prompts(self):
        """设置预定义提示"""
        # 添加常用提示
        self.server.prompt()(self._welcome_prompt)
        self.server.prompt()(self._device_query_prompt)
        self.server.prompt()(self._telemetry_query_prompt)
        self.server.prompt()(self._device_control_prompt)
        self.server.prompt()(self._dashboard_prompt)
        
    async def _welcome_prompt(self) -> List[Dict[str, Any]]:
        """欢迎提示"""
        return common_prompts.welcome_prompt()
    
    async def _device_query_prompt(self) -> List[Dict[str, Any]]:
        """设备查询提示"""
        return common_prompts.device_query_prompt()
    
    async def _telemetry_query_prompt(self) -> List[Dict[str, Any]]:
        """遥测数据查询提示"""
        return common_prompts.telemetry_query_prompt()
    
    async def _device_control_prompt(self) -> List[Dict[str, Any]]:
        """设备控制提示"""
        return common_prompts.device_control_prompt()
    
    async def _dashboard_prompt(self) -> List[Dict[str, Any]]:
        """平台概览提示"""
        return common_prompts.dashboard_prompt()
        
    def check_configuration(self) -> bool:
        """检查配置是否完整"""
        if not config.is_configured():
            logger.warning("未配置ThingsPanel或ThingsVis API认证信息，服务无法访问受保护的API")
            return False
        return True
        
    def run(self, transport: str = 'stdio'):
        """运行服务器"""
        # 重新加载配置，确保环境变量中的设置被应用
        from .config import config
        config.load_config()
        
        if not self.check_configuration():
            logger.error("配置不完整，服务器启动失败")
            print("配置不完整，服务器启动失败。请配置 ThingsPanel Token/API Key 或 ThingsVis Token。")
            print("您可以通过以下方式配置API密钥：")
            print("1. 设置环境变量 THINGSPANEL_TOKEN 或 THINGSPANEL_API_KEY")
            print("2. 创建 ~/.thingspanel/config.json，在 profiles 中分别配置超管和租户管理员的 token")
            return
        
        logger.info(f"ThingsPanel MCP 服务器启动，使用 {transport} 传输")
        self.server.run(transport=transport)
