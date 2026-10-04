"""Telemetry tools with typed point values and timestamps."""

import logging
from typing import Any, Optional

from ..api_client import ThingsPanelClient
from ..tool_results import (
    DeviceTelemetryData,
    DeviceTelemetryResult,
    HistoryPoint,
    TelemetryByKeyData,
    TelemetryByKeyResult,
    TelemetryHistoryData,
    TelemetryHistoryResult,
    TelemetryItem,
    make_error,
)

logger = logging.getLogger(__name__)


def _telemetry_item(raw: dict[str, Any]) -> TelemetryItem:
    return TelemetryItem(
        key=raw.get("key"),
        label=raw.get("label") or raw.get("key"),
        value=raw.get("value"),
        unit=raw.get("unit"),
        timestamp=raw.get("ts"),
    )


async def get_device_telemetry(device_id: str) -> DeviceTelemetryResult:
    """返回设备最新遥测点，保留值的原始 JSON 类型。"""
    client = ThingsPanelClient()
    try:
        result = await client.get_current_telemetry(device_id)
        if result.get("code") != 200:
            return DeviceTelemetryResult(
                ok=False,
                summary="获取设备遥测数据失败。",
                error=make_error(result.get("code"), result.get("message"), "获取设备遥测数据失败。"),
            )

        items = [_telemetry_item(item) for item in (result.get("data") or [])]
        summary = f"已读取设备 {device_id} 的 {len(items)} 个遥测点。" if items else f"设备 {device_id} 暂无遥测数据。"
        return DeviceTelemetryResult(
            ok=True,
            summary=summary,
            data=DeviceTelemetryData(device_id=device_id, items=items),
        )
    except Exception as exc:
        logger.error("获取设备遥测数据出错: %s", exc.__class__.__name__)
        return DeviceTelemetryResult(
            ok=False,
            summary="获取设备遥测数据时发生错误。",
            error=make_error("request_failed", str(exc), "获取设备遥测数据时发生错误。"),
        )


async def get_telemetry_by_key(device_id: str, key: str) -> TelemetryByKeyResult:
    """按遥测标识符读取单个当前值。"""
    client = ThingsPanelClient()
    try:
        result = await client.get_telemetry_by_keys(device_id, [key])
        if result.get("code") != 200:
            return TelemetryByKeyResult(
                ok=False,
                summary="获取遥测数据失败。",
                error=make_error(result.get("code"), result.get("message"), "获取遥测数据失败。"),
            )

        telemetry_data = result.get("data") or []
        item = _telemetry_item(telemetry_data[0]) if telemetry_data else None
        summary = f"已读取设备 {device_id} 的遥测项 {key}。" if item else f"设备 {device_id} 暂无遥测项 {key}。"
        return TelemetryByKeyResult(
            ok=True,
            summary=summary,
            data=TelemetryByKeyData(device_id=device_id, key=key, item=item),
        )
    except Exception as exc:
        logger.error("获取遥测数据出错: %s", exc.__class__.__name__)
        return TelemetryByKeyResult(
            ok=False,
            summary="获取遥测数据时发生错误。",
            error=make_error("request_failed", str(exc), "获取遥测数据时发生错误。"),
        )


async def get_telemetry_history(
    device_id: str,
    key: str,
    time_range: str = "last_1h",
    aggregate_window: str = "no_aggregate",
    aggregate_function: Optional[str] = None,
) -> TelemetryHistoryResult:
    """返回历史数据点；超过 10 点时保留既有抽样行为并明确标注截断。"""
    client = ThingsPanelClient()
    try:
        result = await client.get_telemetry_statistics(
            device_id=device_id,
            key=key,
            time_range=time_range,
            aggregate_window=aggregate_window,
            aggregate_function=aggregate_function,
        )
        if result.get("code") != 200:
            return TelemetryHistoryResult(
                ok=False,
                summary="获取遥测历史数据失败。",
                error=make_error(result.get("code"), result.get("message"), "获取遥测历史数据失败。"),
            )

        data = result.get("data") or {}
        if isinstance(data, list):
            raw_points = data
            start = raw_points[0].get("x") if raw_points else None
            end = raw_points[-1].get("x") if raw_points else None
        else:
            raw_points = data.get("time_series") or []
            time_range_data = data.get("x_time_range") or {}
            start = time_range_data.get("start")
            end = time_range_data.get("end")

        total_points = len(raw_points)
        if isinstance(data, list) or total_points <= 10:
            selected = raw_points
        else:
            step = max(1, total_points // 10)
            selected = raw_points[::step][:10]
        points = [HistoryPoint(timestamp=point.get("x"), value=point.get("y")) for point in selected]
        out_data = TelemetryHistoryData(
            device_id=device_id,
            key=key,
            time_range=time_range,
            aggregate_window=aggregate_window,
            aggregate_function=aggregate_function,
            start=start,
            end=end,
            total_points=total_points,
            points=points,
            truncated=len(points) < total_points,
        )
        return TelemetryHistoryResult(
            ok=True,
            summary=f"设备 {device_id} 的 {key} 有 {total_points} 个历史点，返回 {len(points)} 个。"
            if total_points else f"设备 {device_id} 暂无 {key} 的历史数据。",
            data=out_data,
        )
    except Exception as exc:
        logger.error("获取遥测历史数据出错: %s", exc.__class__.__name__)
        return TelemetryHistoryResult(
            ok=False,
            summary="获取遥测历史数据时发生错误。",
            error=make_error("request_failed", str(exc), "获取遥测历史数据时发生错误。"),
        )
