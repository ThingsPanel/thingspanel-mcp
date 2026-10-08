"""Compact tenant and trend summaries with structured numeric fields."""

import logging

from ..api_client import ThingsPanelClient
from ..tool_results import (
    DeviceTrendData,
    DeviceTrendPoint,
    DeviceTrendResult,
    TenantSummaryData,
    TenantSummaryResult,
    make_error,
)

logger = logging.getLogger(__name__)


async def get_tenant_summary() -> TenantSummaryResult:
    """获取租户设备和消息统计。"""
    client = ThingsPanelClient()
    try:
        tenant_result = await client.get_tenant_id()
        tenant_id = tenant_result.get("data") if tenant_result.get("code") == 200 else None

        devices_result = await client.get_tenant_devices_info()
        if devices_result.get("code") != 200:
            return TenantSummaryResult(
                ok=False,
                summary="获取租户设备统计失败。",
                error=make_error(devices_result.get("code"), devices_result.get("message"), "获取租户设备统计失败。"),
            )

        messages_result = await client.get_message_count()
        message_count = (messages_result.get("data") or {}).get("msg", 0) if messages_result.get("code") == 200 else 0
        stats = devices_result.get("data") or {}
        total = stats.get("device_total", 0)
        online = stats.get("device_on", 0)
        rate = online / total * 100 if total else 0.0
        active = stats.get("device_activity", 0)
        return TenantSummaryResult(
            ok=True,
            summary=f"租户当前有 {total} 台设备，其中 {online} 台在线。",
            data=TenantSummaryData(
                tenant_id=tenant_id,
                device_total=total,
                device_online=online,
                online_rate=rate,
                device_active=active,
                message_count=message_count,
            ),
        )
    except Exception as exc:
        logger.error("获取租户信息出错: %s", exc.__class__.__name__)
        return TenantSummaryResult(
            ok=False,
            summary="获取租户信息时发生错误。",
            error=make_error("request_failed", str(exc), "获取租户信息时发生错误。"),
        )


async def get_device_trend_report() -> DeviceTrendResult:
    """获取最近五个设备在线趋势点。"""
    client = ThingsPanelClient()
    try:
        result = await client.get_device_trend()
        if result.get("code") != 200:
            return DeviceTrendResult(
                ok=False,
                summary="获取设备趋势失败。",
                error=make_error(result.get("code"), result.get("message"), "获取设备趋势失败。"),
            )

        raw_points = ((result.get("data") or {}).get("points") or [])[-5:]
        points = []
        for point in raw_points:
            total = point.get("device_total", 0)
            online = point.get("device_online", 0)
            points.append(DeviceTrendPoint(
                timestamp=point.get("timestamp"),
                device_total=total,
                device_online=online,
                device_offline=point.get("device_offline", 0),
                online_rate=online / total * 100 if total else 0.0,
            ))
        return DeviceTrendResult(
            ok=True,
            summary=f"已读取 {len(points)} 个最近趋势点。" if points else "没有找到设备趋势数据。",
            data=DeviceTrendData(points=points),
        )
    except Exception as exc:
        logger.error("获取设备趋势出错: %s", exc.__class__.__name__)
        return DeviceTrendResult(
            ok=False,
            summary="获取设备趋势时发生错误。",
            error=make_error("request_failed", str(exc), "获取设备趋势时发生错误。"),
        )
