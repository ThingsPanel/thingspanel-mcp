# src/thingspanel_mcp/prompts/common_prompts.py
from typing import Dict, Any, Optional, List

def welcome_prompt() -> List[Dict[str, Any]]:
    """欢迎提示，介绍如何使用ThingsPanel MCP服务"""
    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": "我想了解如何使用ThingsPanel MCP服务"
            }
        },
        {
            "role": "assistant",
            "content": {
                "type": "text",
                "text": """# 欢迎使用ThingsPanel MCP服务

ThingsPanel MCP服务让您可以使用自然语言与ThingsPanel物联网平台交互，轻松管理和查询您的物联网设备和数据。

## 您可以做什么：

1. **查询设备信息**
   - "列出所有设备"
   - "查询设备详情"
   - "检查设备在线状态"

2. **获取遥测数据**
   - "获取设备的当前温度"
   - "查看设备最近一小时的湿度数据"
   - "显示设备的电池电量历史记录"

3. **控制设备**
   - "打开设备的开关"
   - "设置设备温度为25度"
   - "向设备发送重启命令"

4. **查看平台概览**
   - "获取租户概览"
   - "显示设备在线趋势"
   - "统计消息数量"

## 使用示例：

- "请列出我的所有设备"
- "获取设备ID为abc123的详细信息"
- "设备abc123当前的温度是多少？"
- "展示设备abc123最近24小时的温度历史数据"
- "查看租户总览信息"

随时提问，我将帮助您轻松管理和了解您的物联网设备！"""
            }
        }
    ]

def device_query_prompt() -> List[Dict[str, Any]]:
    """设备查询提示模板"""
    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": "如何查询设备信息？"
            }
        },
        {
            "role": "assistant",
            "content": {
                "type": "text",
                "text": """# 设备查询指南

您可以通过以下方式查询ThingsPanel平台上的设备信息：

## 列出设备
- "列出所有设备"
- "显示前10个设备"
- "搜索名称包含'传感器'的设备"

## 查看设备详情
- "获取设备ID为{device_id}的详细信息"
- "查看设备{device_name}的详情"

## 检查设备状态
- "设备{device_id}在线吗？"
- "检查设备{device_name}的状态"
- "哪些设备目前在线？"

## 查询设备属性
- "设备{device_id}的属性有哪些？"
- "显示设备{device_name}的配置信息"

请尝试使用这些查询方式来获取您的设备信息！"""
            }
        }
    ]

def telemetry_query_prompt() -> List[Dict[str, Any]]:
    """遥测数据查询提示模板"""
    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": "如何查询设备的遥测数据？"
            }
        },
        {
            "role": "assistant",
            "content": {
                "type": "text",
                "text": """# 遥测数据查询指南

您可以通过以下方式查询ThingsPanel平台上的设备遥测数据：

## 获取当前数据
- "获取设备{device_id}的当前遥测数据"
- "设备{device_name}的温度是多少？"
- "显示设备{device_id}的湿度值"

## 查询历史数据
- "获取设备{device_id}最近一小时的温度数据"
- "显示设备{device_name}过去24小时的湿度历史"
- "查询设备{device_id}的电池电量趋势"

## 数据聚合与统计
- "计算设备{device_id}今天的平均温度"
- "获取设备{device_name}上周的最高湿度值"
- "统计设备{device_id}本月的运行时间"

可用的时间范围选项：
- 最近5分钟、15分钟、30分钟
- 最近1小时、3小时、6小时、12小时、24小时
- 最近3天、7天、15天、30天、60天、90天
- 最近6个月、1年

请尝试使用这些查询方式来获取您的设备遥测数据！"""
            }
        }
    ]

def device_control_prompt() -> List[Dict[str, Any]]:
    """设备控制提示模板"""
    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": "如何控制设备？"
            }
        },
        {
            "role": "assistant",
            "content": {
                "type": "text",
                "text": """# 设备控制指南

您可以通过以下方式控制ThingsPanel平台上的设备：

## 发送开关命令
- "打开设备{device_id}的开关"
- "关闭设备{device_name}的电源"
- "重启设备{device_id}"

## 设置参数
- "设置设备{device_id}的温度为25℃"
- "将设备{device_name}的湿度阈值调整为60%"
- "修改设备{device_id}的运行模式为自动"

## 执行自定义命令
- "向设备{device_id}发送自定义命令：{command_json}"
- "执行设备{device_name}的固件更新"

例如，发送JSON命令：
向设备abc123发送命令: {"method":"DEVICE_CONTROL","params":{"switch":true}}
请注意，设备控制命令的具体参数取决于您的设备类型和配置。请确保您的命令格式正确，并且设备支持相应的控制功能。"""
            }
        }
    ]

def dashboard_prompt() -> List[Dict[str, Any]]:
    """平台概览提示模板"""
    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": "如何查看平台总体情况？"
            }
        },
        {
            "role": "assistant",
            "content": {
                "type": "text",
                "text": """# 平台概览查询指南

您可以通过以下方式查询ThingsPanel平台的总体情况：

## 租户概览
- "获取租户概览信息"
- "显示租户统计数据"
- "查询平台用户数量"

## 设备统计
- "统计平台设备总数"
- "查看设备在线率"
- "获取设备活跃情况"

## 趋势分析
- "显示设备在线趋势"
- "查看最近24小时的设备活跃度"
- "获取平台消息数量趋势"

## 综合报告
- "生成平台运行报告"
- "展示平台健康状况"
- "获取租户资源使用情况"

这些查询可以帮助您全面了解您的ThingsPanel平台状态和运行情况！"""
            }
        }
    ]