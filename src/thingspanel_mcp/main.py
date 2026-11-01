#!/usr/bin/env python3
import argparse
import os
import logging

from thingspanel_mcp import ThingsPanelServer, config

def main():
    # 设置参数解析
    parser = argparse.ArgumentParser(description='ThingsPanel MCP 服务器')
    parser.add_argument('--token', help='Encore 用户令牌（推荐使用环境变量）')
    parser.add_argument('--base-url', help='Encore API 基础 URL')
    parser.add_argument('--transport', choices=['stdio', 'sse'], default='stdio',
                      help='传输类型 (默认: stdio)')
    parser.add_argument('--verbose', '-v', action='store_true', help='启用详细日志')
    args = parser.parse_args()
    
    # 设置日志级别
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level)
    
    if args.token:
        os.environ['THINGSPANEL_TOKEN'] = args.token
        
    # 设置基础URL
    if args.base_url:
        os.environ['THINGSPANEL_ENCORE_BASE_URL'] = args.base_url
    
    # 重载配置模块以确保环境变量被应用
    from thingspanel_mcp.config import config
    config.load_config()
    
    # 创建并运行服务器
    server = ThingsPanelServer()
    server.run(transport=args.transport)
