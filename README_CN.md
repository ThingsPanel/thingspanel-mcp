# ThingsPanel MCP

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/thingspanel-mcp.svg)](https://pypi.org/project/thingspanel-mcp/)
[![PyPI version](https://badge.fury.io/py/thingspanel-mcp.svg)](https://badge.fury.io/py/thingspanel-mcp)

[ThingsPanel](http://thingspanel.io/) 物联网平台的MCP（Model Context Protocol）服务器。

[English](README.md) | [中文](README_CN.md)

这个MCP服务器将ThingsPanel物联网平台与支持模型上下文协议的AI模型（如Claude、GPT等）集成在一起。它为AI模型提供了一种标准化的方式来：

- 查询ThingsPanel中的设备信息和状态
- 检索设备历史数据进行分析
- 管理设备（创建、更新、删除）
- 访问产品目录和模板
- 监控并响应告警和通知
- 通过ThingsPanel向物联网设备发送命令

通过使用这个MCP服务器，AI助手可以以安全、受控的方式直接与您的物联网设备和数据交互，从而实现强大的应用场景，如自然语言设备控制、数据可视化请求、异常检测以及基于设备数据的智能自动化。

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

## 功能特点

- [x] 设备管理
  - [x] 分页和筛选列出设备
  - [x] 通过ID获取设备详情
  - [x] 创建新设备
  - [x] 更新现有设备
  - [x] 删除设备
  - [ ] 批量设备操作
  - [ ] 设备分组
- [x] 数据检索和分析
  - [x] 查询设备历史数据
  - [x] 按时间范围筛选
  - [x] 按特定属性筛选
  - [x] 获取最新设备数据
  - [ ] 设备数据统计分析
  - [ ] 数据可视化端点
- [x] 产品管理
  - [x] 分页列出产品
  - [x] 获取产品详情
  - [ ] 创建和更新产品
  - [ ] 产品模板管理
- [x] 告警和通知
  - [x] 列出设备告警
  - [x] 按状态、严重性和时间筛选告警
  - [ ] 创建和更新告警
  - [ ] 确认和解决告警
  - [ ] 配置告警规则
- [ ] 命令和控制
  - [ ] 向设备发送命令
  - [ ] 调度设备操作
  - [ ] 批量命令操作
- [x] 集成
  - [x] 模型上下文协议(MCP)支持
  - [x] 传输选项(stdio, SSE)
  - [x] Docker容器支持
  - [ ] Webhook支持
  - [ ] 第三方API集成

工具列表是可配置的，允许您根据需求或上下文窗口限制启用或禁用特定功能。

## 安装

```bash
pip install thingspanel-mcp
```

或从源代码安装：

```bash
git clone https://github.com/yourusername/thingspanel-mcp.git
cd thingspanel-mcp
pip install -e .
```

## 配置

通过环境变量进行配置：

- `THINGSPANEL_URL`：ThingsPanel API URL（默认值：http://thingspanel.io/）
- `THINGSPANEL_API_KEY`：您的ThingsPanel API密钥

### 设置API密钥

API密钥必须正确设置才能与ThingsPanel平台进行身份验证。ThingsPanel使用`x-api-key`请求头进行身份验证。

您可以通过以下几种方式设置API密钥：

1. **环境变量（推荐）**：
   ```bash
   export THINGSPANEL_API_KEY=您的API密钥
   ```

2. **与命令一起内联使用**：
   ```bash
   THINGSPANEL_API_KEY=您的API密钥 thingspanel-mcp
   ```

3. **在.env文件中**：
   在项目目录中创建一个`.env`文件：
   ```
   THINGSPANEL_URL=http://thingspanel.io/
   THINGSPANEL_API_KEY=您的API密钥
   ```

要验证您的API密钥是否正常工作，可以使用直接API调用进行测试：
```bash
curl -H "x-api-key: 您的API密钥" http://thingspanel.io/api/v1/device/group/tree
```

## 使用方法

启动MCP服务器：

```bash
thingspanel-mcp
```

这将使用默认的stdio传输方式启动服务器。您也可以使用SSE传输方式：

```bash
thingspanel-mcp --transport sse
```

查看所有可用选项：

```bash
thingspanel-mcp --help
```

## Docker使用方法

您也可以在Docker容器中运行ThingsPanel MCP：

### 使用Docker Compose（推荐）

1. 在环境中设置您的API密钥：
   ```bash
   export THINGSPANEL_API_KEY=your_api_key
   ```

2. 启动服务：
   ```bash
   docker-compose up -d
   ```

这将同时启动ThingsPanel MCP服务器和用于调试的MCP Inspector。

### 直接使用Docker

1. 构建Docker镜像：
   ```bash
   docker build -t thingspanel-mcp .
   ```

2. 运行容器：
   ```bash
   docker run -p 8000:8000 -e THINGSPANEL_API_KEY=your_api_key thingspanel-mcp
   ```

## 手动测试

您可以使用MCP Inspector对MCP服务器进行手动测试。这将帮助您了解服务器的功能以及它如何响应不同的请求。

### 测试准备

首先，确保您的API密钥已设置在环境中：
```bash
export THINGSPANEL_API_KEY="您的API密钥"
```

然后启动MCP检查器。您有两种选择：

1. 使用内置的inspect命令（推荐）：
```bash
thingspanel-mcp inspect
```

2. 直接使用npx：
```bash
npx @modelcontextprotocol/inspector
```

启动Inspector后，在浏览器中访问 http://localhost:5173。

#### 列出设备
```json
{
    "limit": 10,
    "offset": 0
}
```

#### 获取设备详情
```json
{
    "device_id": "您的设备ID"
}
```

#### 创建设备
```json
{
    "device_data": {
        "deviceNumber": "test-device-001",
        "deviceName": "测试设备001",
        "protocolType": "MQTT",
        "productId": "您的产品ID",
        "description": "这是一个测试设备"
    }
}
```
预期响应：
```json
{
    "code": 200,
    "data": {
        "id": "新创建的设备ID",
        "deviceNumber": "test-device-001",
        "deviceName": "测试设备001",
        // ... 其他设备详情
    }
}
```

#### 更新设备
```json
{
    "device_id": "您的设备ID",
    "device_data": {
        "deviceName": "更新后的设备名称",
        "description": "更新后的设备描述"
    }
}
```
预期响应：
```json
{
    "code": 200,
    "msg": "success"
}
```

#### 删除设备
```json
{
    "device_id": "您的设备ID"
}
```
预期响应：
```json
{
    "code": 200,
    "msg": "success"
}
```

### 参数格式

在MCP Inspector中使用工具时，请确保正确格式化参数：

✅ **正确的**参数格式：
```json
{
  "limit": 10,
  "offset": 0
}
```

❌ **错误的**格式（不要使用嵌套的"arguments"对象）：
```json
{
  "arguments": {
    "limit": 10,
    "offset": 0
  }
}
```

### 测试示例

连接成功后，您可以测试各种可用工具。以下是一些示例：

#### 列出设备

测试设备列表功能：

1. 选择 `list_devices` 工具
2. 输入参数：
   ```json
   {
     "limit": 10,
     "offset": 0
   }
   ```
3. 点击"Execute"（执行）
4. 您应该会看到来自ThingsPanel实例的设备列表响应

#### 获取设备详情

检索特定设备的信息：

1. 选择 `get_device` 工具
2. 输入参数（替换为实际设备ID）：
   ```json
   {
     "device_id": "device123"
   }
   ```
3. 点击"Execute"（执行）
4. 您应该会看到指定设备的详细信息

#### 查询设备数据

检索设备的历史数据：

1. 选择 `get_device_data` 工具
2. 输入参数（替换为实际设备ID）：
   ```json
   {
     "device_id": "device123",
     "limit": 5,
     "attributes": ["temperature", "humidity"]
   }
   ```
3. 点击"Execute"（执行）
4. 您应该会看到指定设备的历史数据点

#### 列出产品

检索产品信息：

1. 选择 `list_products` 工具
2. 输入参数：
   ```json
   {
     "limit": 5
   }
   ```
3. 点击"Execute"（执行）
4. 您应该会看到来自ThingsPanel的产品列表

#### 查看告警

检查设备告警：

1. 选择 `list_alarms` 工具
2. 输入参数：
   ```json
   {
     "limit": 5
   }
   ```
3. 点击"Execute"（执行）
4. 您应该会看到系统中的告警列表

### 预期输出格式

所有响应都遵循标准格式：

```json
{
  "code": 200,
  "data": {
    // 特定于每个工具的结果数据
  },
  "msg": "success"
}
```

错误响应将包含错误详情和非200的状态码。

## 使用MCP Inspector进行调试

MCP Inspector是一个用于调试和测试MCP服务器的有用工具。使用方法：

1. 安装并运行MCP Inspector：
   ```bash
   npx @modelcontextprotocol/inspector
   ```

2. 在浏览器中访问 http://localhost:5173

3. 在Inspector界面中配置连接：
   - 传输类型(Transport Type)：STDIO
   - 命令(Command)：thingspanel-mcp
   - 参数(Arguments)：（留空或根据需要添加选项）

4. 点击"Connect"开始测试您的MCP服务器

或者，直接使用命令启动Inspector：
```bash
npx @modelcontextprotocol/inspector -- thingspanel-mcp
```

## 故障排除

### 访问localhost:8000出现"Not Found"

如果在访问http://localhost:8000时看到"Not Found"错误，这是正常的。MCP服务器不是设计为通过网页浏览器直接访问的。它使用特定协议与AI模型通信。

### MCP Inspector的端口冲突

如果遇到端口冲突错误，如`Error: listen EADDRINUSE: address already in use :::3000`：

1. 使用不同的端口：
   ```bash
   npx @modelcontextprotocol/inspector --port 3001 -- thingspanel-mcp
   ```

2. 查找并终止使用3000端口的进程：
   ```bash
   lsof -i :3000   # 在macOS/Linux上
   kill [PID]      # 通过进程ID终止进程
   ```

### MCP Inspector中的连接错误

如果在尝试从Inspector连接到MCP服务器时遇到连接错误：

1. 确保您的ThingsPanel MCP服务器没有在另一个终端中运行
2. 检查命令和参数是否正确
3. 确保所有必需的环境变量都已设置
4. 尝试使用完整路径：
   ```bash
   npx @modelcontextprotocol/inspector -- $(which thingspanel-mcp)
   ```

## 开发

1. 克隆仓库
2. 安装开发依赖：`pip install -e ".[dev,lint]"`
3. 运行测试：`pytest`

### 使用Makefile

项目包含一个Makefile，用于简化常见任务：

```bash
make install     # 安装开发依赖
make build       # 构建包
make test        # 运行测试
make run         # 运行MCP服务器
make docker-build # 构建Docker镜像
make docker-run  # 使用Docker Compose运行
make docker-stop # 停止Docker Compose服务
make clean       # 清理构建产物
```

## 许可证

Apache License 2.0 