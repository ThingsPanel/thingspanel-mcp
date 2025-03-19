#!/usr/bin/env python3
import argparse
import os
import logging

from thingspanel_mcp import ThingsPanelServer, config

def main():
    # 设置参数解析
    parser = argparse.ArgumentParser(description='ThingsPanel MCP 服务器')
    parser.add_argument('--api-key', help='ThingsPanel API密钥')
    parser.add_argument('--base-url', help='ThingsPanel API基础URL')
    parser.add_argument('--transport', choices=['stdio', 'sse'], default='stdio',
                      help='传输类型 (默认: stdio)')
    parser.add_argument('--verbose', '-v', action='store_true', help='启用详细日志')
    args = parser.parse_args()
    
    # 设置日志级别
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level)
    
    # 设置API密钥
    if args.api_key:
        os.environ['THINGSPANEL_API_KEY'] = args.api_key
        print(f"从命令行设置API密钥: {args.api_key[:5]}...")
        
    # 设置基础URL
    if args.base_url:
        os.environ['THINGSPANEL_BASE_URL'] = args.base_url
        print(f"从命令行设置基础URL: {args.base_url}")
    
    # 重载配置模块以确保环境变量被应用
    from thingspanel_mcp.config import config
    config.load_config()
    
    # 创建并运行服务器
    server = ThingsPanelServer()
    server.run(transport=args.transport)