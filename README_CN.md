# ThingsPanel MCP

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/thingspanel-mcp.svg)](https://pypi.org/project/thingspanel-mcp/)
[![PyPI version](https://badge.fury.io/py/thingspanel-mcp.svg)](https://badge.fury.io/py/thingspanel-mcp)

[ThingsPanel](http://thingspanel.io/) 物联网平台的MCP（Model Context Protocol）服务器。

[English](README.md) | [中文](README_CN.md)

## 🚀 项目简介

ThingsPanel MCP 服务器是一个革新性的智能接口，让您可以：

- 使用自然语言与物联网设备交互
- 轻松获取设备信息
- 实时监控设备性能和状态
- 简单发送设备控制指令
- 分析平台整体统计数据和趋势

## 适用人群

### 目标用户

- **物联网解决方案开发者**：在ThingsPanel物联网平台上构建解决方案并希望集成AI能力的工程师和开发人员
- **AI集成专家**：寻求将AI模型与物联网系统连接的专业人士
- **系统管理员**：负责管理物联网基础设施并希望启用AI驱动的分析和控制的IT人员
- **产品团队**：构建结合物联网和AI功能的产品的团队

### 解决的问题

- **集成复杂性**：消除了在AI模型和物联网平台之间构建自定义集成的需求
- **标准化访问**：为AI模型提供与物联网数据和设备交互的一致接口
- **安全控制**：管理AI访问物联网系统的身份验证和授权
- **降低技术门槛**：降低为现有物联网部署添加AI能力的技术障碍

### 理想应用场景

- **自然语言物联网控制**：使用户能够通过AI助手使用自然语言控制设备
- **智能数据分析**：允许AI模型访问和分析物联网传感器数据以获取洞察
- **异常检测**：将AI模型连接到设备数据流，实现实时异常检测
- **预测性维护**：通过提供设备历史访问，实现AI驱动的预测性维护
- **自动化报告**：创建能够根据请求生成物联网数据报告和可视化的系统
- **运营优化**：使用AI基于历史模式优化设备操作

## ✨ 核心功能

- 🗣️ 自然语言查询
- 📊 全面设备洞察
- 🌡️ 实时遥测数据
- 🎮 便捷设备控制
- 📈 平台全面分析

## 🛠️ 环境准备

- Python 3.8 及以上版本
- ThingsPanel 账户
- ThingsPanel API 密钥

## 📦 安装指南

### 方式一：Pip 安装

```bash
pip install thingspanel-mcp
```

### 方式二：源代码安装

```bash
# 克隆仓库
git clone https://github.com/ThingsPanel/thingspanel-mcp.git

# 进入项目目录
cd thingspanel-mcp

# 安装项目
pip install -e .
```

## 🔐 配置设置

### 配置方式（选择其一）

#### 方式一：命令行直接配置（推荐）

```bash
thingspanel-mcp --api-key "您的API密钥" --base-url "您的ThingsPanel基础URL"
```

#### 方式二：环境变量配置

如果您希望在多次使用时避免重复输入，可以设置环境变量：

```bash
# 在 ~/.bashrc, ~/.zshrc 或对应的 shell 配置文件中添加
export THINGSPANEL_API_KEY="您的API密钥"
export THINGSPANEL_BASE_URL="您的ThingsPanel基础URL"

# 然后运行
source ~/.bashrc  # 或 source ~/.zshrc
```

#### 方式三：Docker启动

```bash
docker run -it --rm thingspanel-mcp --api-key "您的API密钥" --base-url "您的ThingsPanel基础URL"
```

💡 提示：

- API密钥通常在 ThingsPanel 平台的API KEY管理中获取。
- 基础URL指的是您的 ThingsPanel 平台地址，例如 `http://demo.thingspanel.cn/`
- 建议优先使用命令行配置，以保护敏感信息

## 🖥️ Claude 桌面版集成

在您的 Claude 桌面配置文件 (`claude_desktop_config.json`) 中添加以下内容。根据您的操作系统选择合适的配置：

### Windows 配置示例

```json
{
  "mcpServers": {
    "thingspanel": {
      "command": "thingspanel-mcp",
      "args": [
        "--api-key", "您的API密钥",
        "--base-url", "您的基础URL"
      ]
    }
  }
}
```

### macOS 配置示例

```json
{
  "mcpServers": {
    "thingspanel": {
      "command": "/Library/Frameworks/Python.framework/Versions/3.12/bin/thingspanel-mcp",
      "args": [],
      "env": {
        "THINGSPANEL_API_KEY": "您的API密钥",
        "THINGSPANEL_BASE_URL": "您的基础URL"
      }
    }
  }
}
```

### Docker部署配置

```json
{
  "mcpServers": {
    "thingspanel": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "thingspanel-mcp", "--transport", "stdio", "--api-key", "您的API密钥", "--base-url", "您的基础URL"]
    }
  }
}

💡 提示：

- macOS 用户需要使用 Python 可执行文件的完整路径
- 可以通过运行 `which thingspanel-mcp` 命令找到具体路径
- 建议使用环境变量方式配置敏感信息，避免直接暴露在配置文件中
- 请根据您的 Python 安装位置调整路径

## 🤔 交互示例

使用 ThingsPanel MCP 服务器，您现在可以进行如下自然语言查询：

- "我的传感器当前温度是多少？"
- "列出所有活跃设备"
- "打开自动喷灌系统"
- "显示最近24小时的设备活动情况"

## 🛡️ 安全性

- 凭证安全管理
- 使用 ThingsPanel 官方 API
- 支持基于令牌的身份验证

## 许可证

Apache License 2.0

## 🌟 支持我们

如果这个项目对您有帮助，请在 GitHub 上给我们一个星标！⭐
