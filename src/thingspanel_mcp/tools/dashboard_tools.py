# src/thingspanel_mcp/tools/dashboard_tools.py
from typing import Dict, Any
import logging
from ..api_client import ThingsPanelClient

logger = logging.getLogger(__name__)

async def get_tenant_summary() -> str:
    """
    获取租户信息总览
    """
    client = ThingsPanelClient()
    try:
        
        # 获取租户ID
        tenant_id_result = await client.get_tenant_id()
        tenant_id = tenant_id_result.get("data", "未知") if tenant_id_result.get("code") == 200 else "未知"
        
        # 获取设备信息
        devices_info_result = await client.get_tenant_devices_info()
        if devices_info_result.get("code") != 200:
            return f"获取设备信息失败：{devices_info_result.get('message', '未知错误')}"
        
        # 获取消息数量
        message_count_result = await client.get_message_count()
        message_count = message_count_result.get("data", {}).get("msg", 0) if message_count_result.get("code") == 200 else 0
        
        # 解析设备信息
        device_data = devices_info_result.get("data", {})
        device_total = device_data.get("device_total", 0)
        device_on = device_data.get("device_on", 0)
        device_activity = device_data.get("device_activity", 0)
        
        # 计算设备在线率
        online_rate = (device_on / device_total * 100) if device_total > 0 else 0
        
        summary = (
            f"租户ID: {tenant_id}\n\n"
            f"设备统计:\n"
            f"- 设备总数: {device_total}\n"
            f"- 在线设备: {device_on}\n"
            f"- 在线率: {online_rate:.2f}%\n"
            f"- 激活设备: {device_activity}\n\n"
            f"消息统计:\n"
            f"- 总消息数: {message_count}\n"
        )
        
        return summary
    
    except Exception as e:
        logger.error(f"获取租户信息出错: {str(e)}")
        return f"获取租户信息时发生错误: {str(e)}"

async def get_device_trend_report() -> str:
    """
    获取设备在线趋势报告
    """
    client = ThingsPanelClient()
    try:
        result = await client.get_device_trend()
        
        if result.get("code") != 200:
            return f"获取设备趋势失败：{result.get('message', '未知错误')}"
        
        trend_data = result.get("data", {}).get("points", [])
        if not trend_data:
            return "没有找到设备趋势数据。"
        
        # 获取最新的几个数据点
        recent_points = trend_data[-5:] if len(trend_data) > 5 else trend_data
        
        trend_info = []
        for point in recent_points:
            timestamp = point.get("timestamp", "未知")
            device_total = point.get("device_total", 0)
            device_online = point.get("device_online", 0)
            device_offline = point.get("device_offline", 0)
            online_rate = (device_online / device_total * 100) if device_total > 0 else 0
            
            trend_info.append(
                f"时间: {timestamp}\n"
                f"设备总数: {device_total}\n"
                f"在线设备: {device_online}\n"
                f"离线设备: {device_offline}\n"
                f"在线率: {online_rate:.2f}%\n"
            )
        
        return "设备在线趋势报告 (最近时间点):\n\n" + "\n".join(trend_info)
    
    except Exception as e:
        logger.error(f"获取设备趋势出错: {str(e)}")
        return f"获取设备趋势时发生错误: {str(e)}"