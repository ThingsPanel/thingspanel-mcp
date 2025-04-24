# ThingsPanel MCP [![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE) [![Python Version](https://img.shields.io/pypi/pyversions/thingspanel-mcp.svg)](https://pypi.org/project/thingspanel-mcp/) [![PyPI version](https://badge.fury.io/py/thingspanel-mcp.svg)](https://badge.fury.io/py/thingspanel-mcp)
<a href="https://glama.ai/mcp/servers/@ThingsPanel/thingspanel-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@ThingsPanel/thingspanel-mcp/badge" />
</a>

[ThingsPanel](http://thingspanel.io/) IoT Platform's MCP (Model Context Protocol) Server.

[English](README.md) | [中文](README_CN.md)

## 🚀 Project Overview

ThingsPanel MCP Server is an innovative intelligent interface that enables you to:

- Interact with IoT devices using natural language
- Easily retrieve device information
- Monitor device performance and status in real-time
- Simplify device control commands
- Analyze platform-wide statistical data and trends

## Target Audience

### Intended Users

- **IoT Solution Developers**: Engineers and developers building solutions on the ThingsPanel IoT platform and seeking AI integration capabilities
- **AI Integration Experts**: Professionals looking to connect AI models with IoT systems
- **System Administrators**: IT personnel managing IoT infrastructure and wanting to enable AI-driven analysis and control
- **Product Teams**: Teams building products that combine IoT and AI functionality

### Problems Addressed

- **Integration Complexity**: Eliminates the need to create custom integrations between AI models and IoT platforms
- **Standardized Access**: Provides a consistent interface for AI models to interact with IoT data and devices
- **Security Control**: Manages authentication and authorization for AI access to IoT systems
- **Lowered Technical Barriers**: Reduces technical obstacles to adding AI capabilities to existing IoT deployments

### Ideal Application Scenarios

- **Natural Language IoT Control**: Enable users to control devices through AI assistants using natural language
- **Intelligent Data Analysis**: Allow AI models to access and analyze IoT sensor data for insights
- **Anomaly Detection**: Connect AI models to device data streams for real-time anomaly detection
- **Predictive Maintenance**: Enable AI-driven predictive maintenance by providing device history access
- **Automated Reporting**: Create systems that can generate IoT data reports and visualizations on demand
- **Operational Optimization**: Use AI to optimize device operations based on historical patterns

## ✨ Core Features

- 🗣️ Natural Language Querying
- 📊 Comprehensive Device Insights
- 🌡️ Real-time Telemetry Data
- 🎮 Convenient Device Control
- 📈 Platform-wide Analytics

## 🛠️ Prerequisites

- Python 3.8+
- ThingsPanel Account
- ThingsPanel API Key

## 📦 Installation

### Option 1: Pip Installation

```bash
pip install thingspanel-mcp
```

### Option 2: Source Code Installation

```bash
# Clone the repository
git clone https://github.com/ThingsPanel/thingspanel-mcp.git

# Navigate to project directory
cd thingspanel-mcp

# Install the project
pip install -e .
```

## 🔐 Configuration

### Configuration Methods (Choose One)

#### Method 1: Direct Command Line Configuration (Recommended)

```bash
thingspanel-mcp --api-key "Your API Key" --base-url "Your ThingsPanel Base URL"
```

#### Method 2: Environment Variable Configuration

If you want to avoid repeated input, set environment variables:

```bash
# Add to ~/.bashrc, ~/.zshrc, or corresponding shell config file
export THINGSPANEL_API_KEY="Your API Key"
export THINGSPANEL_BASE_URL="Your ThingsPanel Base URL"

# Then run
source ~/.bashrc  # or source ~/.zshrc
```

💡 Tips:

- API keys are typically obtained from the API KEY management in the ThingsPanel platform
- Base URL refers to your ThingsPanel platform address, e.g., `http://demo.thingspanel.cn/`
- Command-line configuration is recommended to protect sensitive information

## 🖥️ Claude Desktop Integration

Add the following to your Claude desktop configuration file (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "thingspanel": {
      "command": "thingspanel-mcp",
      "args": [
        "--api-key", "Your API Key",
        "--base-url", "Your Base URL"
      ]
    }
  }
}
```

## 🤔 Interaction Examples

Using the ThingsPanel MCP Server, you can now make natural language queries such as:

- "What is the current temperature of my sensor?"
- "List all active devices"
- "Turn on the automatic sprinkler system"
- "Show device activity for the last 24 hours"

## 🛡️ Security

- Secure credential management
- Uses ThingsPanel official API
- Supports token-based authentication

## License

Apache License 2.0

## 🌟 Support Us

If this project helps you, please give us a star on GitHub! ⭐
