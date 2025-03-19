# src/thingspanel_mcp/config.py
import os
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        self.base_url = "http://demo.thingspanel.cn"
        self.api_key = None
        self.load_config()
    
    def load_config(self):
        """加载配置，优先使用环境变量，其次使用配置文件"""
        # 从环境变量加载
        self.api_key = os.environ.get("THINGSPANEL_API_KEY")
        if os.environ.get("THINGSPANEL_BASE_URL"):
            self.base_url = os.environ.get("THINGSPANEL_BASE_URL")
        
        # 如果环境变量中没有API密钥，尝试从配置文件加载
        if not self.api_key:
            config_path = os.environ.get(
                "THINGSPANEL_CONFIG_PATH", 
                str(Path.home() / ".thingspanel" / "config.json")
            )
            try:
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        config_data = json.load(f)
                        self.api_key = config_data.get("api_key")
                        if config_data.get("base_url"):
                            self.base_url = config_data.get("base_url")
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
    
    def is_configured(self):
        """检查是否已配置API密钥"""
        return bool(self.api_key)

# 创建全局配置实例
config = Config()