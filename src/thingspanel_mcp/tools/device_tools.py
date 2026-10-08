"""Device lookup tools with stable, machine-readable result schemas."""

import logging
from typing import Any, Optional

from ..api_client import ThingsPanelClient
from ..tool_results import (
    DeviceConfigInfo,
    DeviceDetailData,
    DeviceDetailResult,
    DeviceInfo,
    DeviceItem,
    DeviceListData,
    DeviceListResult,
    DeviceStatusData,
    DeviceStatusResult,
    make_error,
)

logger = logging.getLogger(__name__)


def _as_bool(value: Any) -> Optional[bool]:
    if value is True or value == 1 or value == "1" or value == "enabled":
        return True
    if value is False or value == 0 or value == "0" or value == "disabled":
        return False
    return None


async def list_devices(search: Optional[str] = None, page: int = 1, page_size: int = 10) -> DeviceListResult:
    """按名称或设备编号搜索设备，返回设备字段和分页信息。"""
    client = ThingsPanelClient()
    try:
        result = await client.get_devices(page=page, page_size=page_size, search=search)
        if result.get("code") != 200:
            return DeviceListResult(
                ok=False,
                summary="获取设备列表失败。",
                error=make_error(result.get("code"), result.get("message"), "获取设备列表失败。"),
            )

        result_data = result.get("data") or {}
        raw_devices = result_data.get("list") or []
        devices = [DeviceItem(
            id=item.get("id"),
            name=item.get("name"),
            device_number=item.get("device_number"),
            device_config_name=item.get("device_config_name"),
            access_way=item.get("access_way"),
            is_online=_as_bool(item.get("is_online")),
            activate_flag=item.get("activate_flag"),
            is_enabled=item.get("is_enabled"),
            created_at=item.get("created_at"),
        ) for item in raw_devices]
        total = result_data.get("total", 0)
        return DeviceListResult(
            ok=True,
            summary=f"找到 {total} 个设备，当前显示第 {page} 页。" if devices else "没有找到符合条件的设备。",
            data=DeviceListData(devices=devices, total=total, page=page, page_size=page_size),
        )
    except Exception as exc:
        logger.error("获取设备列表出错: %s", exc.__class__.__name__)
        return DeviceListResult(
            ok=False,
            summary="获取设备列表时发生错误。",
            error=make_error("request_failed", str(exc), "获取设备列表时发生错误。"),
        )


async def get_device_detail(device_id: str) -> DeviceDetailResult:
    """读取设备详情，包括连接、启用、激活和配置信息。"""
    client = ThingsPanelClient()
    try:
        result = await client.get_device_detail(device_id)
        if result.get("code") != 200:
            return DeviceDetailResult(
                ok=False,
                summary="获取设备详情失败。",
                error=make_error(result.get("code"), result.get("message"), "获取设备详情失败。"),
            )

        device = result.get("data") or {}
        if not device:
            return DeviceDetailResult(
                ok=False,
                summary=f"未找到设备 {device_id}。",
                error=make_error("not_found", "设备不存在。", f"未找到设备 {device_id}。"),
            )

        config = device.get("device_config")
        detail = DeviceInfo(
            id=device.get("id"),
            name=device.get("name"),
            device_number=device.get("device_number"),
            is_online=_as_bool(device.get("is_online")),
            activate_flag=device.get("activate_flag"),
            is_enabled=device.get("is_enabled"),
            access_way=device.get("access_way"),
            created_at=device.get("created_at"),
            update_at=device.get("update_at"),
            device_config=DeviceConfigInfo(**{
                key: config.get(key)
                for key in ("name", "device_type", "protocol_type", "voucher_type")
            }) if isinstance(config, dict) else None,
        )
        return DeviceDetailResult(
            ok=True,
            summary=f"已获取设备 {detail.name or device_id} 的详情。",
            data=DeviceDetailData(device=detail),
        )
    except Exception as exc:
        logger.error("获取设备详情出错: %s", exc.__class__.__name__)
        return DeviceDetailResult(
            ok=False,
            summary="获取设备详情时发生错误。",
            error=make_error("request_failed", str(exc), "获取设备详情时发生错误。"),
        )


async def check_device_status(device_id: str) -> DeviceStatusResult:
    """查询设备连接状态。这个接口不代表设备是否启用。"""
    client = ThingsPanelClient()
    try:
        result = await client.get_device_online_status(device_id)
        if result.get("code") != 200:
            return DeviceStatusResult(
                ok=False,
                summary="获取设备连接状态失败。",
                error=make_error(result.get("code"), result.get("message"), "获取设备连接状态失败。"),
            )

        raw_online = (result.get("data") or {}).get("is_online")
        is_online = _as_bool(raw_online)
        status = "online" if is_online is True else "offline" if is_online is False else "unknown"
        label = {"online": "在线", "offline": "离线", "unknown": "未知"}[status]
        return DeviceStatusResult(
            ok=True,
            summary=f"设备 {device_id} 当前连接状态：{label}。",
            data=DeviceStatusData(device_id=device_id, status=status, is_online=is_online),
        )
    except Exception as exc:
        logger.error("检查设备状态出错: %s", exc.__class__.__name__)
        return DeviceStatusResult(
            ok=False,
            summary="检查设备连接状态时发生错误。",
            error=make_error("request_failed", str(exc), "检查设备连接状态时发生错误。"),
        )
