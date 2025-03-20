# src/thingspanel_mcp/server.py
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from mcp.server.fastmcp import FastMCP, Context
from .config import config
from .tools import device_tools, telemetry_tools, dashboard_tools, control_tools
from .prompts import common_prompts

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
        self.server.tool()(device_tools.list_devices)
        self.server.tool()(device_tools.get_device_detail)
        self.server.tool()(device_tools.check_device_status)
        
        # 遥测数据相关工具
        self.server.tool()(telemetry_tools.get_device_telemetry)
        self.server.tool()(telemetry_tools.get_telemetry_by_key)
        self.server.tool()(telemetry_tools.get_telemetry_history)
        
        # 看板相关工具
        self.server.tool()(dashboard_tools.get_tenant_summary)
        self.server.tool()(dashboard_tools.get_device_trend_report)
        
        # 设备控制相关工具
        self.server.tool()(control_tools.get_device_model_info)
        self.server.tool()(control_tools.control_device_telemetry)
        self.server.tool()(control_tools.set_device_attributes)
        self.server.tool()(control_tools.send_device_command)
        self.server.tool()(control_tools.control_device_with_model_check)
        
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
        if not config.api_key:
            logger.warning("API密钥未配置，服务无法正常工作")
            return False
        return True
        
    def run(self, transport: str = 'stdio'):
        """运行服务器"""
        # 重新加载配置，确保环境变量中的设置被应用
        from .config import config
        config.load_config()
        
        if not self.check_configuration():
            logger.error("配置不完整，服务器启动失败")
            print("配置不完整，服务器启动失败。请确保API密钥已正确配置。")
            print("您可以通过以下方式配置API密钥：")
            print("1. 设置环境变量 THINGSPANEL_API_KEY")
            print("2. 创建配置文件 ~/.thingspanel/config.json 并包含 {\"api_key\": \"您的API密钥\"}")
            return
        
        logger.info(f"ThingsPanel MCP 服务器启动，使用 {transport} 传输")
        self.server.run(transport=transport)