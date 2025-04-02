# src/thingspanel_mcp/tools/telemetry_tools.py
from typing import Dict, List, Any, Optional, Union
import logging
import json
from ..api_client import ThingsPanelClient

logger = logging.getLogger(__name__)

async def get_device_telemetry(device_id: str) -> str:
    """
    根据设备ID获取设备最新遥测数据

    参数:
    device_id: 设备ID示例"4f7040db-8a9c-4c81-d85b-fe574b8a3fa9"，如果只知道设备名称，请先模糊搜索列表确认具体是哪个设备ID
    """
    client = ThingsPanelClient()
    try:
        result = await client.get_current_telemetry(device_id)
        
        if result.get("code") != 200:
            return f"获取设备遥测数据失败：{result.get('message', '未知错误')}"
        
        telemetry_data = result.get("data", [])
        if not telemetry_data:
            return f"设备 {device_id} 没有遥测数据。"
        
        telemetry_info = []
        for item in telemetry_data:
            key = item.get("key", "未知")
            value = item.get("value", "未知")
            timestamp = item.get("ts", "未知")
            unit = item.get("unit", "")
            label = item.get("label", key)
            
            telemetry_info.append(
                f"指标: {label} ({key})\n"
                f"值: {value} {unit}\n"
                f"时间: {timestamp}\n"
            )
        
        return f"设备 {device_id} 的遥测数据:\n\n" + "\n".join(telemetry_info)
    
    except Exception as e:
        logger.error(f"获取设备遥测数据出错: {str(e)}")
        return f"获取设备遥测数据时发生错误: {str(e)}"

async def get_telemetry_by_key(device_id: str, key: str) -> str:
    """
    根据指定的key获取设备遥测数据
    
    参数:
    device_id: 设备ID示例"4f7040db-8a9c-4c81-d85b-fe574b8a3fa9"，如果只知道设备名称，请先模糊搜索列表确认具体是哪个设备ID
    key: 要查询的遥测数据键名，如"status"、"temperature";请不要自行猜测，需要从设备物模型查询接口中确认是哪个key
    """
    client = ThingsPanelClient()
    try:
        result = await client.get_telemetry_by_keys(device_id, [key])
        
        if result.get("code") != 200:
            return f"获取遥测数据失败：{result.get('message', '未知错误')}"
        
        telemetry_data = result.get("data", [])
        if not telemetry_data:
            return f"设备 {device_id} 没有key为 {key} 的遥测数据。"
        
        data_item = telemetry_data[0]
        value = data_item.get("value", "未知")
        timestamp = data_item.get("ts", "未知")
        unit = data_item.get("unit", "")
        label = data_item.get("label", key)
        
        return (
            f"设备 {device_id} 的 {label} ({key}) 数据:\n"
            f"值: {value} {unit}\n"
            f"时间: {timestamp}"
        )
    
    except Exception as e:
        logger.error(f"获取遥测数据出错: {str(e)}")
        return f"获取遥测数据时发生错误: {str(e)}"

async def get_telemetry_history(
    device_id: str, 
    key: str, 
    time_range: str = "last_1h",
    aggregate_window: str = "no_aggregate",
    aggregate_function: Optional[str] = None
) -> str:
    """
    获取设备遥测数据历史数据
    
    参数:
    device_id: 设备ID示例"4f7040db-8a9c-4c81-d85b-fe574b8a3fa9"，如果只知道设备名称，请先模糊搜索列表确认具体是哪个设备ID
    key: 要查询的遥测数据键名，如"status"、"temperature";请不要自行猜测，需要从设备物模型查询接口中确认是哪个key
    """
    client = ThingsPanelClient()
    try:
        result = await client.get_telemetry_statistics(
            device_id=device_id,
            key=key,
            time_range=time_range,
            aggregate_window=aggregate_window,
            aggregate_function=aggregate_function
        )
        
        if result.get("code") != 200:
            return f"获取遥测历史数据失败：{result.get('message', '未知错误')}"
        
        data = result.get("data", {})
        time_series = data.get("time_series", [])
        time_range_info = data.get("x_time_range", {})
        
        if not time_series:
            return f"设备 {device_id} 在所选时间范围内没有 {key} 的历史数据。"
        
        # 获取时间范围信息
        start_time = time_range_info.get("start", "未知")
        end_time = time_range_info.get("end", "未知")
        
        # 选取一部分数据点展示（最多10个）
        display_count = min(10, len(time_series))
        step = len(time_series) // display_count if len(time_series) > display_count else 1
        
        data_points = []
        for i in range(0, len(time_series), step):
            if len(data_points) >= display_count:
                break
                
            point = time_series[i]
            data_points.append(f"时间: {point.get('x')}, 值: {point.get('y')}")
        
        time_range_desc = {
            "last_5m": "最近5分钟",
            "last_15m": "最近15分钟",
            "last_30m": "最近30分钟",
            "last_1h": "最近1小时",
            "last_3h": "最近3小时",
            "last_6h": "最近6小时",
            "last_12h": "最近12小时",
            "last_24h": "最近24小时",
            "last_3d": "最近3天",
            "last_7d": "最近7天",
            "last_15d": "最近15天",
            "last_30d": "最近30天",
            "last_60d": "最近60天",
            "last_90d": "最近90天",
            "last_6m": "最近6个月",
            "last_1y": "最近1年",
            "custom": "自定义时间范围"
        }.get(time_range, time_range)
        
        agg_desc = "无聚合" if aggregate_window == "no_aggregate" else f"聚合间隔: {aggregate_window}"
        if aggregate_function and aggregate_window != "no_aggregate":
            agg_func_desc = {
                "avg": "平均值",
                "max": "最大值",
                "min": "最小值",
                "sum": "总和",
                "diff": "差值"
            }.get(aggregate_function, aggregate_function)
            agg_desc += f", 聚合方法: {agg_func_desc}"
        
        return (
            f"设备 {device_id} 的 {key} 历史数据 ({time_range_desc}):\n"
            f"时间范围: {start_time} 至 {end_time}\n"
            f"{agg_desc}\n"
            f"数据点数量: {len(time_series)}\n\n"
            f"数据样例 (显示 {len(data_points)} 个数据点):\n" +
            "\n".join(data_points)
        )
    
    except Exception as e:
        logger.error(f"获取遥测历史数据出错: {str(e)}")
        return f"获取遥测历史数据时发生错误: {str(e)}"