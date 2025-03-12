# ThingsPanel MCP

MCP (Model Control Plane) server for [ThingsPanel](http://demo.thingspanel.cn/) IoT platform.

This MCP server integrates ThingsPanel IoT platform with AI models like Claude, GPT, and others that support the Model Context Protocol. It provides a standardized way for AI models to:

- Query device information and status from ThingsPanel
- Retrieve historical device data for analysis
- Manage devices (create, update, delete)
- Access product catalogs and templates
- Monitor and respond to alarms and notifications
- Send commands to IoT devices through ThingsPanel

By using this MCP server, AI assistants can directly interact with your IoT devices and data in a secure, controlled manner, enabling powerful use cases like natural language device control, data visualization requests, anomaly detection, and intelligent automation based on device data.

## Who is this for?

### Target Audience

- **IoT Solution Developers**: Engineers and developers who are building solutions on the ThingsPanel IoT platform and want to integrate AI capabilities
- **AI Integration Specialists**: Professionals looking to connect AI models with IoT systems
- **System Administrators**: IT staff responsible for managing IoT infrastructure who want to enable AI-powered analytics and control
- **Product Teams**: Teams building products that combine IoT and AI functionalities

### Problems Solved

- **Integration Complexity**: Eliminates the need to build custom integration between AI models and IoT platforms
- **Standardized Access**: Provides a consistent interface for AI models to interact with IoT data and devices
- **Security Control**: Manages authentication and authorization for AI access to IoT systems
- **Technical Barrier Reduction**: Lowers the technical barrier for adding AI capabilities to existing IoT deployments

### Ideal Use Cases

- **Natural Language IoT Control**: Enable users to control devices using natural language through AI assistants
- **Intelligent Data Analysis**: Allow AI models to access and analyze IoT sensor data for insights
- **Anomaly Detection**: Connect AI models to device data streams for real-time anomaly detection
- **Predictive Maintenance**: Enable AI-driven predictive maintenance by providing access to device history
- **Automated Reporting**: Create systems that can generate reports and visualizations of IoT data on request
- **Operational Optimization**: Use AI to optimize device operations based on historical patterns

## Features

- [x] Device Management
  - [x] List devices with pagination and filtering
  - [x] Get device details by ID
  - [x] Create new devices
  - [x] Update existing devices
  - [x] Delete devices
  - [ ] Batch device operations
  - [ ] Device grouping
- [x] Data Retrieval and Analysis
  - [x] Query historical device data
  - [x] Filter by time range
  - [x] Filter by specific attributes
  - [x] Get latest device data
  - [ ] Statistical analysis of device data
  - [ ] Data visualization endpoints
- [x] Product Management
  - [x] List products with pagination
  - [x] Get product details
  - [ ] Create and update products
  - [ ] Product template management
- [x] Alarm and Notification
  - [x] List device alarms
  - [x] Filter alarms by status, severity, and time
  - [ ] Create and update alarms
  - [ ] Acknowledge and resolve alarms
  - [ ] Configure alarm rules
- [ ] Command and Control
  - [ ] Send commands to devices
  - [ ] Schedule device actions
  - [ ] Batch command operations
- [x] Integration
  - [x] Model Context Protocol (MCP) support
  - [x] Transport options (stdio, SSE)
  - [x] Docker container support
  - [ ] Webhook support
  - [ ] Third-party API integrations

The list of tools is configurable, allowing you to enable or disable specific functionalities based on your needs or context window constraints.

## Installation

```bash
pip install thingspanel-mcp
```

Or install from source:

```bash
git clone https://github.com/yourusername/thingspanel-mcp.git
cd thingspanel-mcp
pip install -e .
```

## Configuration

Configuration is done via environment variables:

- `THINGSPANEL_URL`: ThingsPanel API URL (default: http://demo.thingspanel.cn/)
- `THINGSPANEL_API_KEY`: Your ThingsPanel API key

### Setting up your API key

The API key must be set correctly for authentication with the ThingsPanel platform. ThingsPanel uses the `x-api-key` header for authentication.

You can set your API key in several ways:

1. **Environment variable (recommended)**:
   ```bash
   export THINGSPANEL_API_KEY=your_api_key
   ```

2. **Inline with command**:
   ```bash
   THINGSPANEL_API_KEY=your_api_key thingspanel-mcp
   ```

3. **In your .env file**:
   Create a `.env` file in the project directory:
   ```
   THINGSPANEL_URL=http://demo.thingspanel.cn/
   THINGSPANEL_API_KEY=your_api_key
   ```

To verify your API key works correctly, you can test it with a direct API call:
```bash
curl -H "x-api-key: your_api_key" http://demo.thingspanel.cn/api/v1/device/group/tree
```

## Usage

Start the MCP server:

```bash
thingspanel-mcp
```

This will start the server using stdio for transport by default. You can also use SSE:

```bash
thingspanel-mcp --transport sse
```

To see all available options:

```bash
thingspanel-mcp --help
```

## Docker Usage

You can also run ThingsPanel MCP in a Docker container:

### Using Docker Compose (Recommended)

1. Set your API key in the environment:
   ```bash
   export THINGSPANEL_API_KEY=your_api_key
   ```

2. Start the services:
   ```bash
   docker-compose up -d
   ```

This will start both the ThingsPanel MCP server and the MCP Inspector for debugging.

### Using Docker Directly

1. Build the Docker image:
   ```bash
   docker build -t thingspanel-mcp .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 -e THINGSPANEL_API_KEY=your_api_key thingspanel-mcp
   ```

## Manual Testing

First, make sure you have set the API key as an environment variable:
```bash
export THINGSPANEL_API_KEY="your_api_key"
```

Then start the MCP Inspector. You have two options:

1. Using the built-in inspect command (recommended):
```bash
thingspanel-mcp inspect
```

2. Using npx directly:
```bash
npx @modelcontextprotocol/inspector
```

After starting the Inspector, navigate to http://localhost:5173 in your browser.

#### List Devices
```json
{
    "limit": 10,
    "offset": 0
}
```

#### Get Device Details
```json
{
    "device_id": "your_device_id"
}
```

#### Create Device
```json
{
    "device_data": {
        "deviceNumber": "test-device-001",
        "deviceName": "Test Device 001",
        "protocolType": "MQTT",
        "productId": "your_product_id",
        "description": "This is a test device"
    }
}
```
Expected response:
```json
{
    "code": 200,
    "data": {
        "id": "newly_created_device_id",
        "deviceNumber": "test-device-001",
        "deviceName": "Test Device 001",
        // ... other device details
    }
}
```

#### Update Device
```json
{
    "device_id": "your_device_id",
    "device_data": {
        "deviceName": "Updated Device Name",
        "description": "Updated device description"
    }
}
```
Expected response:
```json
{
    "code": 200,
    "msg": "success"
}
```

#### Delete Device
```json
{
    "device_id": "your_device_id"
}
```
Expected response:
```json
{
    "code": 200,
    "msg": "success"
}
```

## Debugging with MCP Inspector

The MCP Inspector is a useful tool for debugging and testing your MCP server. To use it:

1. Install and run the MCP Inspector:
   ```bash
   npx @modelcontextprotocol/inspector
   ```

2. Access the Inspector at http://localhost:5173

3. Configure the connection in the Inspector UI:
   - Transport Type: STDIO
   - Command: thingspanel-mcp
   - Arguments: (leave empty or add options if needed)

4. Click "Connect" to start testing your MCP server

Alternatively, launch the Inspector with your command directly:
```bash
npx @modelcontextprotocol/inspector -- $(which thingspanel-mcp)
```

## Troubleshooting

### "Not Found" on localhost:8000

If you see a "Not Found" error when accessing http://localhost:8000, this is normal. The MCP server is not designed to be accessed directly through a web browser. It communicates using specific protocols for AI models.

### Port conflicts with MCP Inspector

If you encounter a port conflict error like `Error: listen EADDRINUSE: address already in use :::3000`:

1. Use a different port:
   ```bash
   npx @modelcontextprotocol/inspector --port 3001 -- $(which thingspanel-mcp)
   ```

2. Find and terminate the process using port 3000:
   ```bash
   lsof -i :3000   # On macOS/Linux
   kill [PID]      # Kill the process by its ID
   ```

### Connection errors in MCP Inspector

If you encounter connection errors when trying to connect to your MCP server from the Inspector:

1. Ensure your ThingsPanel MCP server isn't already running in another terminal
2. Check that the command and arguments are correct
3. Make sure all required environment variables are set
4. Try using the full path to Python:
   ```bash
   npx @modelcontextprotocol/inspector -- $(which python) -m thingspanel_mcp
   ```

## Development

1. Clone the repository
2. Install development dependencies: `pip install -e ".[dev,lint]"`
3. Run tests: `pytest`

### Using Makefile

The project includes a Makefile to simplify common tasks:

```bash
make install     # Install development dependencies
make build       # Build the package
make test        # Run tests
make run         # Run the MCP server
make docker-build # Build the Docker image
make docker-run  # Run with Docker Compose
make docker-stop # Stop Docker Compose services
make clean       # Clean build artifacts
```

## License

Apache License 2.0