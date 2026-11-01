# src/thingspanel_mcp/server.py
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from mcp.server.fastmcp import FastMCP, Context
from .config import config
from .tools import device_tools, telemetry_tools, dashboard_tools, control_tools
from .prompts import common_prompts
from .api_tools import register_api_tools, load_encore_manifest
from .encore_focused_tools import register_encore_focused_tools
from .encore_asset_tools import register_encore_asset_tools
from .encore_control_tools import register_encore_control_tools

logger = logging.getLogger(__name__)

class ThingsPanelServer:
    """ThingsPanel MCP 服务器"""
    
    def __init__(self, server_name: str = "ThingsPanel"):
        """初始化ThingsPanel MCP服务器"""
        self.server = FastMCP(server_name)
        self._setup_tools()
        self._setup_prompts()
        
    def _setup_tools(self):
        """只注册明确核对过的 Encore 接口；不自动回退旧路由。"""
        native = os.environ.get("THINGSPANEL_ENABLE_NATIVE_METADATA") == "1"
        self.focused_tool_count = register_encore_focused_tools(self.server, include_native=native)
        self.api_tool_count = register_api_tools(self.server, manifest=load_encore_manifest())
        self.asset_tool_count = register_encore_asset_tools(self.server) if native else 0
        self.control_tool_count = register_encore_control_tools(self.server) if native else 0
        
    def _setup_prompts(self):
        """设置预定义提示"""
        # 添加常用提示
        self.server.prompt()(self._encore_prompt)

    async def _encore_prompt(self) -> str:
        """介绍已核对的 Encore 工具和版本依赖。"""
        return "使用 tools/list 查看当前可用的 Encore 工具。设备原生功能仅在服务端部署候选版本并明确启用时可用；写入前确认用户意图，失败或结果未知时不要猜测成功。"
        
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
        if not config.encore_base_url or not any(p.get("thingspanel_token") for p in config.profiles.values()):
            logger.warning("需要明确配置 Encore 地址及用户令牌")
            return False
        return True
        
    def run(self, transport: str = 'stdio'):
        """运行服务器"""
        # 重新加载配置，确保环境变量中的设置被应用
        from .config import config
        config.load_config()
        
        if not self.check_configuration():
            logger.error("配置不完整：请设置 THINGSPANEL_ENCORE_BASE_URL 与 THINGSPANEL_TOKEN")
            return
        
        logger.info(f"ThingsPanel MCP 服务器启动，使用 {transport} 传输")
        self.server.run(transport=transport)
