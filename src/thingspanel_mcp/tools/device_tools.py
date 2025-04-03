# src/thingspanel_mcp/tools/device_tools.py
from typing import Dict, List, Any, Optional
import logging
from ..api_client import ThingsPanelClient

logger = logging.getLogger(__name__)

async def list_devices(search: Optional[str] = None, page: int = 1, page_size: int = 10) -> str:
    """
    可以根据用户说出来的设备名称或设备编号进行模糊搜索，获取设备ID、设备名称、设备编号、在线状态、激活状态、创建时间
    注意：支持大小写不敏感的模糊搜索，不要多次尝试，没搜索到就及时反馈用户
    """
    client = ThingsPanelClient()
    try:
        result = await client.get_devices(page=page, page_size=page_size, search=search)
        
        if result.get("code") != 200:
            return f"获取设备列表失败：{result.get('message', '未知错误')}"
        
        devices = result.get("data", {}).get("list", [])
        total = result.get("data", {}).get("total", 0)
        
        if not devices:
            return "没有找到符合条件的设备。"
        
        device_info = []
        for device in devices:
            status = "在线" if device.get("is_online") == 1 else "离线"
            
            # 检查激活状态
            activate_status = "未激活"
            if device.get("activate_flag") == "active":
                activate_status = "已激活"
                
            device_info.append(
                f"设备ID: {device.get('id')}\n"
                f"设备名称: {device.get('name')}\n"
                f"设备编号: {device.get('device_number')}\n"
                f"设备模板类型: {device.get('device_config_name', '未设置')}\n"
                f"配置类型: {device.get('access_way', '未知')}\n"
                f"在线状态: {status}\n"
                f"激活状态: {activate_status}\n"
                f"创建时间: {device.get('created_at', '未知')}\n"
            )
        
        header = f"共找到 {total} 个设备，当前显示第 {page} 页，每页 {page_size} 条：\n\n"
        return header + "\n".join(device_info)
    
    except Exception as e:
        logger.error(f"获取设备列表出错: {str(e)}")
        return f"获取设备列表时发生错误: {str(e)}"

async def get_device_detail(device_id: str) -> str:
    """
    根据设备ID获取设备详细信息
    
    参数:
    device_id: 设备ID示例"4f7040db-8a9c-4c81-d85b-fe574b8a3fa9"，如果只知道设备名称，请先模糊搜索列表确认具体是哪个设备ID
    """
    client = ThingsPanelClient()
    try:
        result = await client.get_device_detail(device_id)
        
        if result.get("code") != 200:
            return f"获取设备详情失败：{result.get('message', '未知错误')}"
        
        device = result.get("data", {})
        if not device:
            return f"未找到设备 {device_id} 的详情信息。"
        
        is_online = "在线" if device.get("is_online") == 1 else "离线"
        activate_flag = "已激活" if device.get("activate_flag") == "active" else "未激活"
        is_enabled = "已启用" if device.get("is_enabled") == "enabled" else "已禁用"
        
        detail_info = (
            f"设备ID: {device.get('id')}\n"
            f"设备名称: {device.get('name')}\n"
            f"设备编号: {device.get('device_number', '未设置')}\n"
            f"在线状态: {is_online}\n"
            f"激活状态: {activate_flag}\n"
            f"启用状态: {is_enabled}\n"
            f"接入方式: {device.get('access_way', '未知')}\n"
            f"创建时间: {device.get('created_at', '未知')}\n"
            f"更新时间: {device.get('update_at', '未知')}\n"
        )
        
        # 如果有设备配置信息，添加到详情中
        if device.get("device_config"):
            config = device.get("device_config", {})
            detail_info += (
                f"\n设备配置信息:\n"
                f"配置名称: {config.get('name', '未知')}\n"
                f"设备类型: {config.get('device_type', '未知')}\n"
                f"协议类型: {config.get('protocol_type', '未知')}\n"
                f"凭证类型: {config.get('voucher_type', '未知')}\n"
            )
        
        return detail_info
    
    except Exception as e:
        logger.error(f"获取设备详情出错: {str(e)}")
        return f"获取设备详情时发生错误: {str(e)}"

async def check_device_status(device_id: str) -> str:
    """
    检查设备的在线状态

    参数:
    device_id: 设备ID示例"4f7040db-8a9c-4c81-d85b-fe574b8a3fa9"，如果只知道设备名称，请先模糊搜索列表确认具体是哪个设备ID
    """
    client = ThingsPanelClient()
    try:
        result = await client.get_device_online_status(device_id)
        
        if result.get("code") != 200:
            return f"获取设备状态失败：{result.get('message', '未知错误')}"
        
        status_data = result.get("data", {})
        is_online = status_data.get("is_online", 0)
        
        if is_online == 1:
            return f"设备 {device_id} 当前状态：在线"
        else:
            return f"设备 {device_id} 当前状态：离线"
    
    except Exception as e:
        logger.error(f"检查设备状态出错: {str(e)}")
        return f"检查设备状态时发生错误: {str(e)}"