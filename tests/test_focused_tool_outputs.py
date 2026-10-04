import asyncio

from mcp.server.fastmcp import FastMCP

from thingspanel_mcp.tools import control_tools, dashboard_tools, device_tools, telemetry_tools


FOCUSED_TOOLS = [
    device_tools.list_devices,
    device_tools.get_device_detail,
    device_tools.check_device_status,
    telemetry_tools.get_device_telemetry,
    telemetry_tools.get_telemetry_by_key,
    telemetry_tools.get_telemetry_history,
    dashboard_tools.get_tenant_summary,
    dashboard_tools.get_device_trend_report,
    control_tools.get_device_model_info,
    control_tools.control_device_telemetry,
    control_tools.set_device_attributes,
    control_tools.send_device_command,
    control_tools.get_device_command_status,
    control_tools.control_device_with_model_check,
]


def test_focused_tools_publish_object_output_schemas():
    server = FastMCP("focused-output-test")
    for function in FOCUSED_TOOLS:
        server.tool(structured_output=True)(function)

    tools = {tool.name: tool for tool in server._tool_manager.list_tools()}
    assert len(tools) == 14
    for tool in tools.values():
        assert tool.output_schema["type"] == "object"
        assert {"ok", "summary", "error", "data"}.issubset(tool.output_schema["properties"])


def test_list_devices_returns_typed_empty_page(monkeypatch):
    class FakeClient:
        async def get_devices(self, **kwargs):
            return {"code": 200, "data": {"list": [], "total": 0}}

    monkeypatch.setattr(device_tools, "ThingsPanelClient", FakeClient)
    result = asyncio.run(device_tools.list_devices(search="bedroom"))

    assert result.ok is True
    assert result.summary == "没有找到符合条件的设备。"
    assert result.data.devices == []
    assert result.data.total == 0
    assert result.data.page == 1


def test_mcp_tool_call_returns_structured_content(monkeypatch):
    class FakeClient:
        async def get_devices(self, **kwargs):
            return {"code": 200, "data": {"list": [{"id": "device-1", "name": "灯", "is_online": 1}], "total": 1}}

    monkeypatch.setattr(device_tools, "ThingsPanelClient", FakeClient)
    server = FastMCP("structured-call-test")
    server.tool(structured_output=True)(device_tools.list_devices)

    async def call_tool():
        _, structured = await server._tool_manager.call_tool(
            "list_devices", {"search": "灯"}, convert_result=True
        )
        return structured

    result = asyncio.run(call_tool())
    assert result["ok"] is True
    assert result["data"]["devices"][0]["is_online"] is True
    assert isinstance(result["data"]["devices"][0]["is_online"], bool)


def test_telemetry_values_keep_json_types(monkeypatch):
    class FakeClient:
        async def get_current_telemetry(self, device_id):
            return {"code": 200, "data": [{"key": "switch", "value": 1, "ts": 123, "unit": "", "label": "开关"}]}

    monkeypatch.setattr(telemetry_tools, "ThingsPanelClient", FakeClient)
    result = asyncio.run(telemetry_tools.get_device_telemetry("device-1"))

    assert result.ok is True
    item = result.data.items[0]
    assert item.key == "switch"
    assert item.value == 1
    assert isinstance(item.value, int)
    assert item.timestamp == 123


def test_send_command_returns_receipt_id_and_status(monkeypatch):
    class FakeClient:
        async def _request(self, method, endpoint, params=None, json_data=None):
            assert method == "POST"
            assert endpoint == "/api/v1/command/datas/pub"
            return {"code": 200, "data": {"message_id": "message-123", "status": "accepted"}}

    monkeypatch.setattr(control_tools, "ThingsPanelClient", FakeClient)
    result = asyncio.run(control_tools.send_device_command(
        "device-1", {"method": "switch", "params": {"value": 1}}
    ))

    assert result.ok is True
    assert result.data.message_id == "message-123"
    assert result.data.status == "accepted"
    assert result.data.accepted is True


def test_command_status_returns_typed_state(monkeypatch):
    class FakeClient:
        async def _request(self, method, endpoint, params=None, json_data=None):
            assert method == "GET"
            assert endpoint.endswith("/status/message-123")
            return {"code": 200, "data": {
                "message_id": "message-123",
                "status": "device_succeeded",
                "raw_status": "3",
                "response": "{\"result\":0}",
            }}

    monkeypatch.setattr(control_tools, "ThingsPanelClient", FakeClient)
    result = asyncio.run(control_tools.get_device_command_status("message-123"))

    assert result.ok is True
    assert result.data.status == "device_succeeded"
    assert result.data.raw_status == "3"
    assert result.data.message_id == "message-123"
