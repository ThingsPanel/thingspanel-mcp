import asyncio
import json

import httpx
from mcp.server.fastmcp import FastMCP

from thingspanel_mcp.api_client import ThingsPanelClient
from thingspanel_mcp.api_tools import register_api_tools, load_encore_manifest
from thingspanel_mcp.config import config
from thingspanel_mcp.server import ThingsPanelServer


def setup_config(monkeypatch):
    monkeypatch.setattr(config, "encore_base_url", "http://127.0.0.1:4444")
    monkeypatch.setattr(config, "profiles", {"default": {"thingspanel_token": "test-token"}})


def test_default_server_registers_encore_without_legacy_or_candidate(monkeypatch):
    monkeypatch.delenv("THINGSPANEL_ENABLE_NATIVE_METADATA", raising=False)
    names = {tool.name for tool in ThingsPanelServer().server._tool_manager.list_tools()}
    assert "encore_thingmodel_list" in names
    assert "encore_device_list" not in names
    assert "list_devices" not in names
    assert "send_device_command" not in names


def test_candidate_requires_explicit_enablement(monkeypatch):
    monkeypatch.setenv("THINGSPANEL_ENABLE_NATIVE_METADATA", "1")
    names = {tool.name for tool in ThingsPanelServer().server._tool_manager.list_tools()}
    assert "encore_device_list" in names and "encore_list_devices" in names
    assert "encore_upload_template_image" in names and "encore_download_metadata_artifact" in names
    assert "send_native_device_command" in names and "get_native_command_receipt" in names


def test_northbound_tools_require_explicit_deployment_opt_in(monkeypatch):
    monkeypatch.delenv("THINGSPANEL_ENABLE_NORTHBOUND", raising=False)
    default = {o["tool_name"] for o in load_encore_manifest()["operations"] if o["enabled"]}
    monkeypatch.setenv("THINGSPANEL_ENABLE_NORTHBOUND", "1")
    enabled = {o["tool_name"] for o in load_encore_manifest()["operations"] if o["enabled"]}
    assert "encore_northbound_overview" not in default
    assert "encore_northbound_overview" in enabled


def test_encore_header_body_etag_and_unknown_write(monkeypatch):
    setup_config(monkeypatch)
    seen = []
    def handler(request):
        seen.append(request)
        if request.url.path.endswith("/timeout"):
            raise httpx.ReadTimeout("fixture timeout", request=request)
        if request.url.path.endswith("/server-error"):
            return httpx.Response(500, json={"message":"fixture failure"})
        return httpx.Response(200, headers={"ETag": '"rev-1"'}, json={"data": {"id": "a"}})
    client = ThingsPanelClient(transport=httpx.MockTransport(handler))
    async def run():
        got = await client.request_api("encore", "PATCH", "/api/v2/devices/:id", path_params={"id":"a"}, body={"name":"x"}, idempotency_key="update-key-1", if_match='"rev-1"', outcome_sensitive=True)
        assert got["etag"] == '"rev-1"' and got["ok"]
        assert seen[-1].headers["authorization"] == "Bearer test-token"
        assert seen[-1].headers["idempotency-key"] == "update-key-1"
        assert seen[-1].headers["if-match"] == '"rev-1"'
        assert "x-tenant-id" not in seen[-1].headers
        failed = await client.request_api("encore", "POST", "/api/v2/timeout", body={}, outcome_sensitive=True)
        assert failed["error"]["type"] == "outcome_unknown"
        failed = await client.request_api("encore", "POST", "/api/v2/server-error", body={}, outcome_sensitive=True)
        assert failed["error"]["type"] == "outcome_unknown"
    asyncio.run(run())


def test_automation_body_idempotency_and_confirmation():
    class Client:
        def __init__(self): self.calls = []
        async def request_api(self, **kwargs): self.calls.append(kwargs); return {"ok": True}
    client = Client()
    operation = next(o for o in load_encore_manifest()["operations"] if o["tool_name"] == "encore_rule_create")
    server = FastMCP("fixture")
    register_api_tools(server, client=client, manifest={"schema_version":1, "operations":[operation]})
    async def run():
        manager = server._tool_manager
        preview = await manager.call_tool("encore_rule_create", {"body":{"secret":"private"}})
        assert preview["confirmation_required"] and "private" not in json.dumps(preview)
        invalid = await manager.call_tool("encore_rule_create", {"confirmed":True,"body":{},"idempotency_key":"short"})
        assert not invalid["ok"] and not client.calls
        result = await manager.call_tool("encore_rule_create", {"confirmed":True,"body":{"definition":{}},"idempotency_key":"rule-key-1"})
        assert result["ok"] and client.calls[0]["body"]["request_id"] == "rule-key-1"
        assert "idempotency_key" not in client.calls[0] and client.calls[0]["outcome_sensitive"]
    asyncio.run(run())


def test_native_mutation_requires_etag_and_passes_it_to_client(monkeypatch):
    monkeypatch.setenv("THINGSPANEL_ENABLE_NATIVE_METADATA", "1")
    class Client:
        def __init__(self): self.calls = []
        async def request_api(self, **kwargs): self.calls.append(kwargs); return {"ok": True, "etag": '"v2"'}
    client = Client()
    operation = next(o for o in load_encore_manifest()["operations"] if o["tool_name"] == "encore_device_update")
    server = FastMCP("native-fixture")
    register_api_tools(server, client=client, manifest={"schema_version": 1, "operations": [operation]})
    async def run():
        manager = server._tool_manager
        base = {"path_params": {"deviceID": "d1"}, "body": {"name": "x"}, "confirmed": True, "idempotency_key": "update-key-1"}
        failed = await manager.call_tool("encore_device_update", base)
        assert failed["error"]["type"] == "missing_if_match" and not client.calls
        result = await manager.call_tool("encore_device_update", {**base, "if_match": '"v1"'})
        assert result["ok"] and client.calls[0]["if_match"] == '"v1"'
        assert client.calls[0]["idempotency_key"] == "update-key-1"
    asyncio.run(run())
