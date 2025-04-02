from typing import Dict, List, Any, Optional, Union
import logging
import json
from ..api_client import ThingsPanelClient

logger = logging.getLogger(__name__)

async def get_device_model_info(device_id: str, model_type: str = "all") -> str:
    """
    获取设备物模型信息
    
    参数:
        device_id: 设备ID示例"4f7040db-8a9c-4c81-d85b-fe574b8a3fa9"，如果只知道设备名称，请先模糊搜索列表确认具体是哪个设备ID
        model_type: 物模型类型，可选值：'all'、'telemetry'、'attributes'、'commands'、'events'
    
    返回:
        格式化的物模型信息文本
    """
    client = ThingsPanelClient()
    try:
        # 首先获取设备详情，找到设备模板ID
        device_detail = await client.get_device_detail(device_id)
        
        if device_detail.get("code") != 200:
            return f"获取设备详情失败：{device_detail.get('message', '未知错误')}"
        
        device_data = device_detail.get("data", {})
        
        # 从device_config字段中获取设备模板ID
        device_config = device_data.get("device_config", {})
        device_template_id = device_config.get("device_template_id")
        
        if not device_template_id:
            return f"设备 {device_id} 未关联设备模板，无法获取物模型信息。设备配置信息：{json.dumps(device_config, ensure_ascii=False)}"
        
        formatted_info = [f"# 设备 {device_id} 物模型信息\n"]
        formatted_info.append(f"设备模板ID: {device_template_id}\n")
        
        # 确定需要查询的模型类型
        model_types = []
        if model_type.lower() == "all":
            model_types = ["telemetry", "attributes", "commands", "events"]
        else:
            model_types = [model_type.lower()]
        
        # 查询每种模型类型
        for type_name in model_types:
            endpoint = f"/api/v1/device/model/{type_name}"
            
            # 查询指定类型的物模型
            model_result = await client._request("GET", endpoint, params={
                "page": 1,
                "page_size": 100,
                "device_template_id": device_template_id
            })
            
            if model_result.get("code") != 200:
                formatted_info.append(f"\n## {type_name.capitalize()} 查询失败\n")
                formatted_info.append(f"错误信息: {model_result.get('message', '未知错误')}\n")
                continue
            
            # 提取模型列表
            model_list = model_result.get("data", {}).get("list", [])
            
            # 显示类型标题
            type_display_map = {
                "telemetry": "遥测",
                "attributes": "属性",
                "commands": "命令",
                "events": "事件"
            }
            type_display = type_display_map.get(type_name, type_name.capitalize())
            formatted_info.append(f"\n## {type_display} ({type_name})\n")
            
            if not model_list:
                formatted_info.append(f"没有找到任何{type_display}定义\n")
                continue
            
            # 处理命令类型的特殊情况
            if type_name == "commands":
                for item in model_list:
                    item_name = item.get("data_name", "未知")
                    item_id = item.get("data_identifier", "未知")
                    
                    formatted_info.append(f"### {item_name} (`{item_id}`)\n")
                    
                    # 处理命令参数
                    params_str = item.get("params", "[]")
                    try:
                        params = json.loads(params_str) if isinstance(params_str, str) else params_str
                    except json.JSONDecodeError:
                        params = []
                    
                    if params and isinstance(params, list):
                        formatted_info.append("参数列表:\n")
                        for param in params:
                            if isinstance(param, dict):
                                param_name = param.get("name", "")
                                param_type = param.get("type", "")
                                param_desc = param.get("description", "")
                                param_required = "是" if param.get("required", False) else "否"
                                
                                formatted_info.append(f"- **{param_name}** (类型: {param_type}, 必填: {param_required})")
                                if param_desc:
                                    formatted_info.append(f"  描述: {param_desc}")
                    
                    # 生成命令示例
                    formatted_info.append("\n使用示例:")
                    example_params = {}
                    if params and isinstance(params, list):
                        for param in params:
                            if isinstance(param, dict) and "name" in param:
                                # 根据类型生成示例值
                                param_type = param.get("type", "").lower()
                                if param_type == "string":
                                    example_params[param["name"]] = "value"
                                elif param_type == "number":
                                    example_params[param["name"]] = 0
                                elif param_type == "boolean":
                                    example_params[param["name"]] = False
                                else:
                                    example_params[param["name"]] = "value"
                    
                    example_cmd = {
                        "method": item_id,
                        "params": example_params
                    }
                    formatted_info.append(f"```json\n{json.dumps(example_cmd, ensure_ascii=False, indent=2)}\n```\n")
            else:
                # 处理其他类型的物模型
                for item in model_list:
                    item_name = item.get("data_name", "未知")
                    item_id = item.get("data_identifier", "未知")
                    data_type = item.get("data_type", "未知")
                    unit = item.get("unit", "")
                    read_write = item.get("read_write_flag", "")
                    
                    rw_display = ""
                    if read_write == "R":
                        rw_display = "只读"
                    elif read_write == "W":
                        rw_display = "只写"
                    elif read_write == "RW":
                        rw_display = "可读写"
                    
                    unit_display = f", 单位: {unit}" if unit else ""
                    rw_display = f", 权限: {rw_display}" if rw_display else ""
                    
                    formatted_info.append(f"- **{item_name}** (标识符: `{item_id}`, 类型: {data_type}{unit_display}{rw_display})")
        
        return "\n".join(formatted_info)
    
    except Exception as e:
        logger.error(f"获取设备物模型信息出错: {str(e)}")
        return f"获取设备物模型信息时发生错误: {str(e)}"

async def control_device_telemetry(device_id: str, control_data: Union[Dict[str, Any], str]) -> str:
    """
    发送遥测数据控制设备 - 通用接口，可用于控制任何类型的遥测数据
    
    参数:
        device_id: 设备ID示例"4f7040db-8a9c-4c81-d85b-fe574b8a3fa9"，如果只知道设备名称，请先模糊搜索列表确认具体是哪个设备ID
        control_data: 控制数据，格式如 {"temperature": 28.5, "light": 2000, "switch": true}
    """
    client = ThingsPanelClient()
    try:
        # 处理不同格式的输入
        if isinstance(control_data, str):
            # 尝试解析为JSON
            try:
                control_json = json.loads(control_data)
            except json.JSONDecodeError:
                # 不是JSON格式，尝试解析为key=value格式
                if "=" in control_data:
                    key, value = control_data.split("=", 1)
                    try:
                        # 尝试将值转换为适当的类型
                        if value.lower() == "true":
                            parsed_value = True
                        elif value.lower() == "false":
                            parsed_value = False
                        elif value.isdigit():
                            parsed_value = int(value)
                        elif "." in value and all(part.isdigit() for part in value.split(".", 1)):
                            parsed_value = float(value)
                        else:
                            parsed_value = value
                        control_json = {key.strip(): parsed_value}
                    except:
                        control_json = {key.strip(): value.strip()}
                else:
                    return f"控制数据格式错误，请提供有效的格式: JSON或key=value"
        else:
            control_json = control_data
        
        # 按照API要求，确保value是JSON字符串
        data = {
            "device_id": device_id,
            "value": json.dumps(control_json)
        }
        
        # 发送请求
        result = await client._request("POST", "/api/v1/telemetry/datas/pub", json_data=data)
        
        if result.get("code") != 200:
            return f"发送遥测控制命令失败：{result.get('message', '未知错误')}"
        
        return f"成功向设备 {device_id} 发送遥测控制命令: {json.dumps(control_json, ensure_ascii=False)}"
    
    except Exception as e:
        logger.error(f"发送遥测控制命令出错: {str(e)}")
        return f"发送遥测控制命令时发生错误: {str(e)}"

async def set_device_attributes(device_id: str, attribute_data: Union[Dict[str, Any], str]) -> str:
    """
    设置设备属性 - 通用接口，可用于设置任何类型的设备属性
    
    参数:
        device_id: 设备ID示例"4f7040db-8a9c-4c81-d85b-fe574b8a3fa9"，如果只知道设备名称，请先模糊搜索列表确认具体是哪个设备ID
        attribute_data: 属性数据，格式如 {"ip": "127.0.0.1", "mac": "xx:xx:xx:xx:xx:xx", "port": 1883}
    """
    client = ThingsPanelClient()
    try:
        # 处理不同格式的输入
        if isinstance(attribute_data, str):
            # 尝试解析为JSON
            try:
                attribute_json = json.loads(attribute_data)
            except json.JSONDecodeError:
                # 不是JSON格式，尝试解析为key=value格式
                if "=" in attribute_data:
                    key, value = attribute_data.split("=", 1)
                    attribute_json = {key.strip(): value.strip()}
                else:
                    return f"属性数据格式错误，请提供有效的格式: JSON或key=value"
        else:
            attribute_json = attribute_data
        
        # 按照API要求，确保value是JSON字符串
        data = {
            "device_id": device_id,
            "value": json.dumps(attribute_json)
        }
        
        # 发送请求
        result = await client._request("POST", "/api/v1/attribute/datas/pub", json_data=data)
        
        if result.get("code") != 200:
            return f"设置设备属性失败：{result.get('message', '未知错误')}"
        
        return f"成功设置设备 {device_id} 的属性: {json.dumps(attribute_json, ensure_ascii=False)}"
    
    except Exception as e:
        logger.error(f"设置设备属性出错: {str(e)}")
        return f"设置设备属性时发生错误: {str(e)}"

async def send_device_command(device_id: str, command_data: Union[Dict[str, Any], str], command_identifier: Optional[str] = None) -> str:
    """
    向设备发送命令
    
    参数:
        device_id: 设备ID示例"4f7040db-8a9c-4c81-d85b-fe574b8a3fa9"，如果只知道设备名称，请先模糊搜索列表确认具体是哪个设备ID
        command_data: 命令数据，格式如 {"method": "ReSet", "params": {"switch": 1, "light": "close"}}
        command_identifier: 命令标识符，如果提供则使用此标识符
    
    注意:
        在发送命令前，应先使用get_device_model_info函数查询设备物模型，
        确保命令名称和参数符合设备物模型要求。
    """
    client = ThingsPanelClient()
    try:
        # 处理不同格式的输入
        if isinstance(command_data, str):
            # 尝试解析为JSON
            try:
                command_json = json.loads(command_data)
            except json.JSONDecodeError:
                return f"命令数据格式错误，请提供有效的JSON格式。建议先使用get_device_model_info查询设备支持的命令。"
        else:
            command_json = command_data
        
        # 提取方法名，用于日志和提示
        method_name = "未知"
        if isinstance(command_json, dict) and "method" in command_json:
            method_name = command_json.get("method")
        
        # 添加物模型检查提示
        logger.info(f"准备向设备 {device_id} 发送 {method_name} 命令，请确保已通过get_device_model_info检查过设备物模型")
        
        # 从命令数据中提取标识符，如果没有提供
        if not command_identifier:
            if isinstance(command_json, dict) and "method" in command_json:
                command_identifier = command_json.get("method")
            else:
                command_identifier = "command"  # 使用默认值
        
        # 按照API要求，确保value是JSON字符串
        data = {
            "device_id": device_id,
            "value": json.dumps(command_json),
            "Identify": command_identifier
        }
        
        # 发送请求
        result = await client._request("POST", "/api/v1/command/datas/pub", json_data=data)
        
        if result.get("code") != 200:
            return f"发送设备命令失败：{result.get('message', '未知错误')}。建议检查设备物模型确认命令格式是否正确。"
        
        return f"成功向设备 {device_id} 发送命令: {json.dumps(command_json, ensure_ascii=False)}"
    
    except Exception as e:
        logger.error(f"发送设备命令出错: {str(e)}")
        return f"发送设备命令时发生错误: {str(e)}"

async def control_device_with_model_check(device_id: str, command_type: str, command_data: Union[Dict[str, Any], str]) -> str:
    """
    先查询物模型，然后再发送控制命令的标准流程
    
    参数:
        device_id: 设备ID示例"4f7040db-8a9c-4c81-d85b-fe574b8a3fa9"，如果只知道设备名称，请先模糊搜索列表确认具体是哪个设备ID
        command_type: 命令类型，可选值：'telemetry'、'attribute'、'command'
        command_data: 命令数据
    
    返回:
        物模型信息和命令执行结果
    """
    # 映射命令类型到物模型类型
    model_type_map = {
        'telemetry': 'telemetry',
        'attribute': 'attributes',
        'command': 'commands'
    }
    
    # 获取对应的物模型类型
    model_type = model_type_map.get(command_type.lower())
    if not model_type:
        return f"不支持的命令类型: {command_type}，请选择 'telemetry'、'attribute' 或 'command'"
    
    # 查询对应类型的物模型
    model_info = await get_device_model_info(device_id, model_type=model_type)
    
    # 根据命令类型选择控制方法
    control_result = ""
    if command_type.lower() == 'telemetry':
        control_result = await control_device_telemetry(device_id, command_data)
    elif command_type.lower() == 'attribute':
        control_result = await set_device_attributes(device_id, command_data)
    elif command_type.lower() == 'command':
        if isinstance(command_data, dict) and "method" in command_data:
            control_result = await send_device_command(device_id, command_data)
        else:
            return f"命令数据格式错误，command类型必须包含method字段。请参考物模型调整命令格式。\n\n物模型信息:\n{model_info}"
    
    # 返回物模型信息和控制结果
    return f"设备物模型信息:\n{model_info}\n\n控制结果:\n{control_result}" 