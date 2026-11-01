# src/thingspanel_mcp/__init__.py
import logging
from .server import ThingsPanelServer
from .config import config

# 设置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger("httpx").setLevel(logging.WARNING)

# 导出主要类和函数
__all__ = ['ThingsPanelServer', 'config']

# 版本信息
__version__ = '0.2.0.dev0'
