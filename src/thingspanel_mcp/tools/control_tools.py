"""Device model, control, and command receipt tools."""

import json
import logging
from typing import Any, Dict, List, Optional, Union

from ..api_client import ThingsPanelClient
from ..tool_results import (
    CommandStatusData,
    CommandStatusResult,
    DeviceModelData,
    DeviceModelResult,
    ModelCheckedControlData,
    ModelCheckedControlResult,
    ModelDefinition,
    OperationData,
    OperationResult,
    make_error,
)

logger = logging.getLogger(__name__)
MODEL_TYPES = ("telemetry", "attributes", "commands", "events")


def _parse_object(value: Union[Dict[str, Any], str], *, allow_pair: bool = True) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str):
        raise ValueError("输入必须是 JSON 对象或字符串")
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        if not allow_pair or "=" not in value:
            raise ValueError("输入格式无效，请提供 JSON 对象或 key=value")
        key, raw_value = value.split("=", 1)
        raw_value = raw_value.strip()
        if raw_value.lower() in ("true", "false"):
            parsed_value: Any = raw_value.lower() == "true"
        else:
            try:
                parsed_value = int(raw_value)
            except ValueError:
                try:
                    parsed_value = float(raw_value)
                except ValueError:
                    parsed_value = raw_value
        return {key.strip(): parsed_value}
    if not isinstance(parsed, dict):
        raise ValueError("输入必须是 JSON 对象")
    return parsed


async def get_device_model_info(device_id: str, model_type: str = "all") -> DeviceModelResult:
    """读取设备模板及其遥测、属性、命令和事件定义。"""
    client = ThingsPanelClient()
    try:
        device_detail = await client.get_device_detail(device_id)
        if device_detail.get("code") != 200:
            return DeviceModelResult(
                ok=False,
                summary="获取设备详情失败，无法读取物模型。",
                error=make_error(device_detail.get("code"), device_detail.get("message"), "获取设备详情失败。"),
            )
        device_data = device_detail.get("data") or {}
        device_config = device_data.get("device_config") or {}
        template_id = device_config.get("device_template_id")
        if not template_id:
            return DeviceModelResult(
                ok=False,
                summary=f"设备 {device_id} 未关联设备模板。",
                error=make_error("template_missing", "设备未关联设备模板。", "设备未关联设备模板。"),
            )

        requested = list(MODEL_TYPES) if model_type.lower() == "all" else [model_type.lower()]
        if any(name not in MODEL_TYPES for name in requested):
            return DeviceModelResult(
                ok=False,
                summary="物模型类型参数无效。",
                error=make_error("invalid_model_type", "支持 all、telemetry、attributes、commands、events。", "物模型类型参数无效。"),
            )

        definitions: Dict[str, List[ModelDefinition]] = {name: [] for name in requested}
        failures = []
        for name in requested:
            result = await client._request("GET", f"/api/v1/device/model/{name}", params={
                "page": 1,
                "page_size": 100,
                "device_template_id": template_id,
            })
            if result.get("code") != 200:
                failures.append(f"{name}: {result.get('message', 'query failed')}")
                continue
            entries = (result.get("data") or {}).get("list") or []
            for entry in entries:
                params = entry.get("params", [])
                if isinstance(params, str):
                    try:
                        params = json.loads(params)
                    except json.JSONDecodeError:
                        params = []
                definitions[name].append(ModelDefinition(
                    data_name=entry.get("data_name"),
                    data_identifier=entry.get("data_identifier"),
                    data_type=entry.get("data_type"),
                    unit=entry.get("unit"),
                    read_write_flag=entry.get("read_write_flag"),
                    params=params if isinstance(params, list) else [],
                ))

        model_data = DeviceModelData(
            device_id=device_id,
            device_template_id=template_id,
            model_type=model_type.lower(),
            definitions=definitions,
        )
        if failures:
            return DeviceModelResult(
                ok=False,
                summary=f"物模型部分读取失败：{'; '.join(failures)}",
                data=model_data,
                error=make_error("partial_failure", "; ".join(failures), "部分物模型读取失败。"),
            )
        count = sum(len(items) for items in definitions.values())
        return DeviceModelResult(
            ok=True,
            summary=f"已读取设备 {device_id} 的 {count} 条物模型定义。",
            data=model_data,
        )
    except Exception as exc:
        logger.error("获取设备物模型出错: %s", exc.__class__.__name__)
        return DeviceModelResult(
            ok=False,
            summary="获取设备物模型时发生错误。",
            error=make_error("request_failed", str(exc), "获取设备物模型时发生错误。"),
        )


async def control_device_telemetry(device_id: str, control_data: Union[Dict[str, Any], str]) -> OperationResult:
    """向设备发布可写遥测控制值。返回平台受理结果，不表示设备已执行。"""
    client = ThingsPanelClient()
    try:
        values = _parse_object(control_data)
        result = await client._request("POST", "/api/v1/telemetry/datas/pub", json_data={
            "device_id": device_id,
            "value": json.dumps(values),
        })
        if result.get("code") != 200:
            return OperationResult(
                ok=False,
                summary="遥测控制请求失败。",
                error=make_error(result.get("code"), result.get("message"), "遥测控制请求失败。"),
            )
        return OperationResult(
            ok=True,
            summary=f"设备 {device_id} 的遥测控制请求已受理。",
            data=OperationData(device_id=device_id, operation="telemetry_control", request=values,
                               accepted=True, status="accepted"),
        )
    except ValueError as exc:
        return OperationResult(ok=False, summary="控制数据格式错误。",
                               error=make_error("invalid_input", str(exc), "控制数据格式错误。"))
    except Exception as exc:
        logger.error("发送遥测控制出错: %s", exc.__class__.__name__)
        return OperationResult(ok=False, summary="发送遥测控制时发生错误。",
                               error=make_error("request_failed", str(exc), "发送遥测控制时发生错误。"))


async def set_device_attributes(device_id: str, attribute_data: Union[Dict[str, Any], str]) -> OperationResult:
    """设置设备属性并返回平台受理状态。"""
    client = ThingsPanelClient()
    try:
        values = _parse_object(attribute_data)
        result = await client._request("POST", "/api/v1/attribute/datas/pub", json_data={
            "device_id": device_id,
            "value": json.dumps(values),
        })
        if result.get("code") != 200:
            return OperationResult(
                ok=False,
                summary="设置设备属性失败。",
                error=make_error(result.get("code"), result.get("message"), "设置设备属性失败。"),
            )
        return OperationResult(
            ok=True,
            summary=f"设备 {device_id} 的属性设置请求已受理。",
            data=OperationData(device_id=device_id, operation="attribute_set", request=values,
                               accepted=True, status="accepted"),
        )
    except ValueError as exc:
        return OperationResult(ok=False, summary="属性数据格式错误。",
                               error=make_error("invalid_input", str(exc), "属性数据格式错误。"))
    except Exception as exc:
        logger.error("设置设备属性出错: %s", exc.__class__.__name__)
        return OperationResult(ok=False, summary="设置设备属性时发生错误。",
                               error=make_error("request_failed", str(exc), "设置设备属性时发生错误。"))


async def send_device_command(
    device_id: str,
    command_data: Union[Dict[str, Any], str],
    command_identifier: Optional[str] = None,
) -> OperationResult:
    """下发命令；返回 message_id 供 get_device_command_status 查询回执。"""
    client = ThingsPanelClient()
    try:
        command = _parse_object(command_data, allow_pair=False)
        method_name = command.get("method")
        identifier = command_identifier or method_name or "command"
        params = command.get("params")
        request = {"method": identifier, "params": params}
        body = {"device_id": device_id, "Identify": identifier}
        if params is not None:
            body["value"] = json.dumps(params)
        result = await client._request("POST", "/api/v1/command/datas/pub", json_data=body)
        if result.get("code") != 200:
            return OperationResult(
                ok=False,
                summary="设备命令下发失败。",
                error=make_error(result.get("code"), result.get("message"), "设备命令下发失败。"),
            )
        receipt = result.get("data") if isinstance(result.get("data"), dict) else result
        message_id = receipt.get("message_id")
        status = receipt.get("status", "accepted")
        summary = "命令已受理，可查询设备回执。" if message_id else "命令已受理，但服务端未返回回执 ID。"
        return OperationResult(
            ok=True,
            summary=summary,
            data=OperationData(device_id=device_id, operation="command", request=request,
                               accepted=True, message_id=message_id, status=status),
        )
    except ValueError as exc:
        return OperationResult(ok=False, summary="命令数据格式错误。",
                               error=make_error("invalid_input", str(exc), "命令数据格式错误。"))
    except Exception as exc:
        logger.error("发送设备命令出错: %s", exc.__class__.__name__)
        return OperationResult(ok=False, summary="发送设备命令时发生错误。",
                               error=make_error("request_failed", str(exc), "发送设备命令时发生错误。"))


async def get_device_command_status(message_id: str) -> CommandStatusResult:
    """按下发返回的 message_id 查询设备命令回执状态。"""
    client = ThingsPanelClient()
    try:
        result = await client._request("GET", f"/api/v1/command/datas/status/{message_id}")
        if result.get("code") != 200:
            return CommandStatusResult(
                ok=False,
                summary="查询命令回执失败。",
                error=make_error(result.get("code"), result.get("message"), "查询命令回执失败。"),
            )
        response = result.get("data") if isinstance(result.get("data"), dict) else result
        status = response.get("status", "unknown")
        allowed = {"accepted", "published", "publish_failed", "device_succeeded", "device_failed", "timeout", "not_found", "unknown"}
        if status not in allowed:
            status = "unknown"
        labels = {
            "accepted": "已受理，等待发布或设备回执",
            "published": "已发布，等待设备回执",
            "publish_failed": "发布失败",
            "device_succeeded": "设备回执成功",
            "device_failed": "设备回执失败",
            "timeout": "等待设备回执超时",
            "not_found": "未找到该命令回执",
            "unknown": "命令状态未知",
        }
        return CommandStatusResult(
            ok=True,
            summary=f"命令 {message_id}：{labels[status]}。",
            data=CommandStatusData(
                message_id=response.get("message_id", message_id),
                status=status,
                raw_status=response.get("raw_status"),
                error_message=response.get("error_message"),
                created_at=response.get("created_at"),
                response=response.get("response"),
            ),
        )
    except Exception as exc:
        logger.error("查询命令回执出错: %s", exc.__class__.__name__)
        return CommandStatusResult(ok=False, summary="查询命令回执时发生错误。",
                                   error=make_error("request_failed", str(exc), "查询命令回执时发生错误。"))


async def control_device_with_model_check(
    device_id: str,
    command_type: str,
    command_data: Union[Dict[str, Any], str],
) -> ModelCheckedControlResult:
    """先读取物模型，再执行指定类型的设备控制。"""
    model_type = {"telemetry": "telemetry", "attribute": "attributes", "command": "commands"}.get(command_type.lower())
    if not model_type:
        return ModelCheckedControlResult(
            ok=False,
            summary="不支持的控制类型。",
            error=make_error("invalid_command_type", "支持 telemetry、attribute、command。", "不支持的控制类型。"),
        )

    model_result = await get_device_model_info(device_id, model_type=model_type)
    if not model_result.ok or model_result.data is None:
        return ModelCheckedControlResult(
            ok=False,
            summary=model_result.summary,
            error=model_result.error,
        )

    try:
        if command_type.lower() == "telemetry":
            operation_result = await control_device_telemetry(device_id, command_data)
        elif command_type.lower() == "attribute":
            operation_result = await set_device_attributes(device_id, command_data)
        else:
            command = _parse_object(command_data, allow_pair=False)
            if "method" not in command:
                raise ValueError("command 类型必须包含 method 字段")
            operation_result = await send_device_command(device_id, command)

        data = ModelCheckedControlData(
            device_id=device_id,
            command_type=command_type.lower(),
            model=model_result.data,
            operation=operation_result.data,
        )
        return ModelCheckedControlResult(
            ok=operation_result.ok,
            summary=f"物模型校验完成。{operation_result.summary}",
            data=data,
            error=operation_result.error,
        )
    except ValueError as exc:
        return ModelCheckedControlResult(
            ok=False,
            summary="控制参数格式错误。",
            error=make_error("invalid_input", str(exc), "控制参数格式错误。"),
        )
