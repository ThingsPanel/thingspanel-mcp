import asyncio

from mcp.server.fastmcp import FastMCP

from thingspanel_mcp.encore_focused_tools import register_encore_focused_tools


class Recorder:
    def __init__(self, result=None):
        self.calls = []
        self.result = result or {"ok": True, "status": 200, "data": {"data": {"items": []}}}

    async def request_api(self, **kwargs):
        self.calls.append(kwargs)
        return self.result


def manager(client):
    server = FastMCP("encore-focused-test")
    assert register_encore_focused_tools(server, client) == 9
    return server._tool_manager


def call(m, name, args):
    return asyncio.run(m.call_tool(name, args))


def test_device_list_targets_native_api_and_preserves_envelope():
    client = Recorder({"ok": True, "status": 200, "data": {"data": {"items": [{"id": "d1"}], "total": 1}, "meta": {"requestId": "r1"}}})
    result = call(manager(client), "encore_list_devices", {"page": 2, "page_size": 25, "search": "sensor"})
    assert result["ok"] is True
    assert result["data"]["meta"]["requestId"] == "r1"
    assert client.calls == [{"service": "encore", "method": "GET", "endpoint": "/api/v2/devices", "path_params": None, "query": {"page": 2, "pageSize": 25, "search": "sensor"}, "profile": "default"}]


def test_reading_query_and_validations():
    client = Recorder()
    m = manager(client)
    result = call(m, "encore_list_device_readings", {"device_id": "d1", "kind": "attribute", "identifier": "voltage", "page_size": 50})
    assert result["ok"] is True
    assert client.calls[-1]["endpoint"] == "/api/v2/devices/:deviceID/readings"
    assert client.calls[-1]["path_params"] == {"deviceID": "d1"}
    assert client.calls[-1]["query"] == {"page": 1, "pageSize": 50, "kind": "attribute", "identifier": "voltage", "latestOnly": "true"}
    for name, args in [("encore_list_devices", {"page": 0}), ("encore_list_devices", {"page_size": 101}), ("encore_list_device_readings", {"device_id": "d1", "kind": "unknown"}), ("encore_get_thing_model_version", {"model_id": "m1", "revision": 0})]:
        assert call(m, name, args)["ok"] is False
    assert len(client.calls) == 1


def test_unavailable_candidate_and_runtime_failure_are_not_offline():
    for status in (404, 503):
        client = Recorder({"ok": False, "status": status, "error": {"code": "unavailable"}})
        result = call(manager(client), "encore_get_device_runtime_state", {"device_id": "d1"})
        assert result["ok"] is False and result["status"] == status
        assert "offline" not in str(result).lower()
        assert len(client.calls) == 1 and client.calls[0]["endpoint"] == "/api/v2/devices/:deviceID/runtime-state"


def test_thing_model_paths_and_profile():
    client = Recorder()
    m = manager(client)
    assert call(m, "encore_get_thing_model_version", {"model_id": "m1", "revision": 3, "profile": "tenant-a"})["ok"]
    assert client.calls[0]["endpoint"] == "/api/v2/thing-models/:modelID/versions/:publishedRevision"
    assert client.calls[0]["path_params"] == {"modelID": "m1", "publishedRevision": 3}
    assert client.calls[0]["profile"] == "tenant-a"
    assert call(m, "encore_list_thing_models", {"page_size": 201})["ok"] is False
    assert len(client.calls) == 1


def test_unavailable_client_exception_does_not_leak_credentials():
    class Broken:
        async def request_api(self, **kwargs):
            raise ValueError("secret-token-must-not-appear")

    result = call(manager(Broken()), "encore_get_device", {"device_id": "d1"})
    assert result["ok"] is False
    assert "secret-token-must-not-appear" not in str(result)


def test_telemetry_history_passes_native_contract_and_rejects_invalid_shape():
    client = Recorder()
    m = manager(client)
    args = {"device_id": "d1", "identifier": "temperature", "from_time": "2026-01-01T00:00:00Z", "to_time": "2026-01-01T01:00:00Z", "aggregation": "avg", "window": "5m"}
    assert call(m, "encore_list_device_readings", args)["ok"]
    assert client.calls[-1]["query"] == {"page": 1, "pageSize": 20, "kind": "telemetry", "identifier": "temperature", "from": args["from_time"], "to": args["to_time"], "aggregation": "avg", "window": "5m"}
    assert not call(m, "encore_list_device_readings", {**args, "kind": "attribute"})["ok"]
    assert len(client.calls) == 1


def test_latest_telemetry_and_events_use_distinct_query_modes():
    client = Recorder()
    m = manager(client)
    assert call(m, "encore_list_device_readings", {"device_id": "d1"})["ok"]
    assert client.calls[-1]["query"]["latestOnly"] == "true"
    assert call(m, "encore_list_device_readings", {"device_id": "d1", "kind": "event"})["ok"]
    assert "latestOnly" not in client.calls[-1]["query"]
