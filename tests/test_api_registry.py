import asyncio
from collections import Counter

from mcp.server.fastmcp import FastMCP

from thingspanel_mcp.api_tools import load_api_manifest, register_api_tools


class RecordingClient:
    def __init__(self):
        self.calls = []

    async def request_api(self, **kwargs):
        self.calls.append(kwargs)
        return {"ok": True, "status": 200, "data": {"probe": True}}


def test_manifest_tool_names_are_unique_and_enabled_paths_are_supported():
    manifest = load_api_manifest()
    enabled = [op for op in manifest["operations"] if op["enabled"]]
    names = [op["tool_name"] for op in enabled]

    assert len(names) == len(set(names))
    assert all(len(name) <= 64 for name in names)
    assert all(op["method"] in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"} for op in enabled)
    assert {op["service"] for op in enabled} == {"thingspanel", "thingsvis"}


def test_each_enabled_operation_is_registered_and_invokes_its_exact_route():
    manifest = load_api_manifest()
    operations = [op for op in manifest["operations"] if op["enabled"]]
    recorder = RecordingClient()
    server = FastMCP("api-registry-test")
    registered = register_api_tools(server, client=recorder, manifest=manifest)
    manager = server._tool_manager
    tools = {tool.name: tool for tool in manager.list_tools()}

    assert registered == len(operations)
    assert set(tools) == {op["tool_name"] for op in operations}

    async def exercise_all():
        for op in operations:
            path_params = {name: "test-id" for name in op["path_parameters"]}
            args = {"path_params": path_params, "query": {}, "profile": "default"}
            if op["destructive"]:
                args.update({"body": {"test": True}, "confirmed": True})
            result = await manager.call_tool(op["tool_name"], args)
            assert result["ok"] is True, op["tool_name"]

    asyncio.run(exercise_all())
    assert len(recorder.calls) == len(operations)
    for operation, call in zip(operations, recorder.calls):
        assert call["service"] == operation["service"]
        assert call["method"] == operation["method"]
        assert call["endpoint"] == operation["path"]
        assert call["path_params"] == {name: "test-id" for name in operation["path_parameters"]}
        assert call["stream"] == operation.get("stream")


def test_write_tool_requires_explicit_confirmation_and_path_parameters():
    manifest = load_api_manifest()
    operation = next(op for op in manifest["operations"] if op["enabled"] and op["method"] == "POST")
    recorder = RecordingClient()
    server = FastMCP("confirmation-test")
    register_api_tools(server, client=recorder, manifest={"schema_version": 1, "operations": [operation]})
    tool = server._tool_manager.get_tool(operation["tool_name"])

    async def no_confirmation():
        return await server._tool_manager.call_tool(operation["tool_name"], {})

    result = asyncio.run(no_confirmation())
    assert result["confirmation_required"] is True
    assert recorder.calls == []

    parameterized = next(op for op in manifest["operations"] if op["enabled"] and op["path_parameters"])
    server2 = FastMCP("path-validation-test")
    register_api_tools(server2, client=recorder, manifest={"schema_version": 1, "operations": [parameterized]})
    missing = asyncio.run(server2._tool_manager.call_tool(parameterized["tool_name"], {}))
    assert missing["error"]["type"] == "missing_path_parameter"
    assert recorder.calls == []


def test_stream_read_limits_are_validated_before_dispatch():
    manifest = load_api_manifest()
    operation = next(op for op in manifest["operations"] if op["enabled"] and op["stream"])
    recorder = RecordingClient()
    server = FastMCP("stream-limits-test")
    register_api_tools(server, client=recorder, manifest={"schema_version": 1, "operations": [operation]})
    invalid = asyncio.run(server._tool_manager.call_tool(operation["tool_name"], {"stream_seconds": 31}))
    assert invalid["error"]["type"] == "invalid_request"
    assert recorder.calls == []


def test_catch_all_path_parameters_are_required_and_dispatched():
    manifest = load_api_manifest()
    operation = next(op for op in manifest["operations"] if op["enabled"] and "*" in op["path"])
    assert operation["path_parameters"]
    recorder = RecordingClient()
    server = FastMCP("catch-all-path-test")
    register_api_tools(server, client=recorder, manifest={"schema_version": 1, "operations": [operation]})
    missing = asyncio.run(server._tool_manager.call_tool(operation["tool_name"], {}))
    assert missing["error"]["type"] == "missing_path_parameter"
    valid = asyncio.run(server._tool_manager.call_tool(
        operation["tool_name"], {"path_params": {operation["path_parameters"][0]: "test.bin"}}
    ))
    assert valid["ok"] is True
    assert recorder.calls[0]["path_params"][operation["path_parameters"][0]] == "test.bin"
