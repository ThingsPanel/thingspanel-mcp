import asyncio
import json
from contextlib import asynccontextmanager

import websockets.asyncio.client

import httpx
import pytest

from thingspanel_mcp.api_client import ThingsPanelClient
from thingspanel_mcp.config import config


def test_thingspanel_token_profile_rewrites_proxy_path_and_refreshes_response_token():
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={"code": 200, "data": {"id": "dev-1"}}, headers={"New-Token": "rotated-token"})

    config.base_url = "http://localhost:5002"
    config.api_prefix = "/proxy-default"
    config.profiles = {"tenant_admin": {"thingspanel_token": "tp-jwt"}}
    client = ThingsPanelClient(transport=httpx.MockTransport(handler))
    result = asyncio.run(client.request_api(
        "thingspanel", "GET", "/api/v1/device/:id",
        path_params={"id": "dev/1"}, profile="tenant_admin",
    ))

    request = requests[0]
    assert request.url.raw_path == b"/proxy-default/device/dev%2F1"
    assert request.headers["x-token"] == "tp-jwt"
    assert request.headers["authorization"] == "Bearer tp-jwt"
    assert result["data"]["data"]["id"] == "dev-1"
    assert config.profiles["tenant_admin"]["thingspanel_token"] == "rotated-token"


def test_thingspanel_api_key_and_thingsvis_bearer_use_separate_headers():
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={"ok": True})

    config.profiles = {
        "tenant_admin": {"thingspanel_api_key": "tenant-key", "thingsvis_token": "thingsvis-jwt"}
    }
    config.base_url = "http://localhost:9999"
    config.api_prefix = "/api/v1"
    config.thingsvis_base_url = "http://localhost:8000"
    config.thingsvis_api_prefix = "/api/v1"
    client = ThingsPanelClient(transport=httpx.MockTransport(handler))

    async def run_calls():
        await client.request_api("thingspanel", "GET", "/api/v1/board", profile="tenant_admin")
        await client.request_api("thingsvis", "GET", "/api/v1/dashboards", profile="tenant_admin")

    asyncio.run(run_calls())
    assert requests[0].headers["x-api-key"] == "tenant-key"
    assert "authorization" not in requests[0].headers
    assert requests[1].headers["authorization"] == "Bearer thingsvis-jwt"
    assert "x-token" not in requests[1].headers


def test_http_errors_are_returned_without_logging_credentials():
    def handler(request):
        return httpx.Response(403, json={"message": "forbidden"})

    config.profiles = {"default": {"thingsvis_token": "secret-token"}}
    config.thingsvis_base_url = "http://localhost:8000"
    config.thingsvis_api_prefix = "/api/v1"
    client = ThingsPanelClient(transport=httpx.MockTransport(handler))
    result = asyncio.run(client.request_api("thingsvis", "GET", "/api/v1/projects"))

    assert result == {"ok": False, "status": 403, "error": {"message": "forbidden"}}
    assert "secret-token" not in json.dumps(result)


def test_thingspanel_business_error_wrapped_in_http_200_is_reported_as_failure():
    def handler(request):
        return httpx.Response(200, json={"code": 201001, "message": "no permission"})

    config.base_url = "http://localhost:9999"
    config.api_prefix = "/api/v1"
    config.profiles = {"tenant_user": {"thingspanel_token": "tenant-jwt"}}
    client = ThingsPanelClient(transport=httpx.MockTransport(handler))
    result = asyncio.run(client.request_api(
        "thingspanel", "GET", "/api/v1/system/metrics/current", profile="tenant_user",
    ))

    assert result == {
        "ok": False,
        "status": 200,
        "error": {"code": 201001, "message": "no permission"},
    }


def test_sse_stream_returns_bounded_events():
    def handler(request):
        assert request.headers["authorization"] == "Bearer thingsvis-jwt"
        return httpx.Response(200, text="event: message\ndata: connected\n\nevent: heartbeat\ndata: 1\n\n")

    config.profiles = {"default": {"thingsvis_token": "thingsvis-jwt"}}
    config.thingsvis_base_url = "http://localhost:8000"
    config.thingsvis_api_prefix = "/api/v1"
    client = ThingsPanelClient(transport=httpx.MockTransport(handler))
    result = asyncio.run(client.request_api(
        "thingsvis", "GET", "/api/v1/events", stream="sse", stream_messages=1,
    ))

    assert result["ok"] is True
    assert result["data"]["events"] == [{"event": "message", "data": "connected"}]


def test_websocket_stream_sends_server_side_auth_in_first_message(monkeypatch):
    sent = []

    class FakeWebSocket:
        async def send(self, data):
            sent.append(json.loads(data))

        async def recv(self):
            return '{"online":true}'

    @asynccontextmanager
    async def fake_connect(url, **kwargs):
        assert url == "ws://localhost:9999/api/v1/device/online/status/ws"
        yield FakeWebSocket()

    monkeypatch.setattr(websockets.asyncio.client, "connect", fake_connect)
    config.base_url = "http://localhost:9999"
    config.api_prefix = "/api/v1"
    config.profiles = {"tenant_user": {"thingspanel_token": "tenant-jwt"}}
    client = ThingsPanelClient()
    result = asyncio.run(client.request_api(
        "thingspanel", "GET", "/api/v1/device/online/status/ws",
        body={"device_id": "d-1"}, profile="tenant_user", stream="websocket",
        stream_messages=1, stream_seconds=1,
    ))

    assert sent == [{"device_id": "d-1", "token": "tenant-jwt"}]
    assert result["ok"] is True
    assert result["data"]["messages"] == ['{"online":true}']


def test_multipart_upload_uses_configured_field_and_file(tmp_path):
    upload = tmp_path / "payload.bin"
    upload.write_bytes(b"test-payload")
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(201, json={"uploaded": True})

    config.thingsvis_base_url = "http://localhost:8000"
    config.thingsvis_api_prefix = "/api/v1"
    config.profiles = {"default": {"thingsvis_token": "tv-jwt"}}
    client = ThingsPanelClient(transport=httpx.MockTransport(handler))
    result = asyncio.run(client.request_api(
        "thingsvis", "POST", "/api/v1/uploads", body={"folder": "reports"},
        file_path=str(upload), upload_field="asset", profile="default",
    ))

    assert result["status"] == 201
    assert b'name="asset"' in requests[0].content
    assert b"test-payload" in requests[0].content
    assert b'name="folder"' in requests[0].content


def test_missing_profile_returns_configuration_error_without_request():
    config.profiles = {"tenant_user": {"thingspanel_token": "user-jwt"}}
    client = ThingsPanelClient(transport=httpx.MockTransport(lambda request: httpx.Response(200)))
    with pytest.raises(KeyError, match="未知认证配置 profile"):
        asyncio.run(client.request_api("thingspanel", "GET", "/api/v1/device", profile="unknown"))


def test_thingsvis_sso_uses_profile_token_and_discards_caller_identity():
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={"accessToken": "thingsvis-issued-token"})

    config.thingsvis_base_url = "http://localhost:8000"
    config.thingsvis_api_prefix = "/api/v1"
    config.profiles = {
        "tenant_user": {
            "thingspanel_token": "verified-thingspanel-jwt",
            "thingsvis_token": "existing-thingsvis-jwt",
        }
    }
    client = ThingsPanelClient(transport=httpx.MockTransport(handler))
    result = asyncio.run(client.request_api(
        "thingsvis", "POST", "/api/v1/auth/sso",
        body={"platform": "evil", "platformToken": "forged", "role": "SUPER_ADMIN",
              "userInfo": {"id": "admin", "tenantId": "other-tenant"}},
        profile="tenant_user",
    ))

    assert result["ok"] is True
    assert json.loads(requests[0].content) == {
        "platform": "thingspanel", "platformToken": "verified-thingspanel-jwt",
    }


def test_thingsvis_sso_requires_thingspanel_token_in_profile():
    config.profiles = {"tenant_user": {"thingsvis_token": "tv-jwt"}}
    client = ThingsPanelClient(transport=httpx.MockTransport(lambda request: httpx.Response(200)))
    with pytest.raises(KeyError, match="缺少 ThingsPanel JWT"):
        asyncio.run(client.request_api("thingsvis", "POST", "/api/v1/auth/sso", profile="tenant_user"))


def test_thingsvis_internal_routes_use_only_internal_token_header():
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={"ok": True})

    config.thingsvis_base_url = "http://localhost:8000"
    config.thingsvis_api_prefix = "/api/v1"
    config.profiles = {"default": {"thingsvis_internal_secret": "internal-secret"}}
    client = ThingsPanelClient(transport=httpx.MockTransport(handler))
    result = asyncio.run(client.request_api(
        "thingsvis", "POST", "/api/internal/market-dashboards/import",
        body={"package": "example"},
    ))

    assert result["ok"] is True
    assert requests[0].headers["x-internal-token"] == "internal-secret"


def test_thingsvis_open_dashboards_prioritizes_api_key_but_app_management_uses_user_jwt():
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={"data": []})

    config.thingsvis_base_url = "http://localhost:8000"
    config.thingsvis_api_prefix = "/api/v1"
    config.profiles = {
        "tenant_admin": {
            "thingsvis_token": "session-jwt",
            "thingsvis_open_api_key": "tvk_open-key",
        }
    }
    client = ThingsPanelClient(transport=httpx.MockTransport(handler))

    async def exercise():
        await client.request_api("thingsvis", "GET", "/api/open/v1/dashboards", profile="tenant_admin")
        await client.request_api("thingsvis", "GET", "/api/open/v1/apps", profile="tenant_admin")

    asyncio.run(exercise())
    assert requests[0].headers["x-api-key"] == "tvk_open-key"
    assert "authorization" not in requests[0].headers
    assert requests[1].headers["authorization"] == "Bearer session-jwt"
    assert "x-api-key" not in requests[1].headers


def test_thingsvis_open_dashboard_does_not_misuse_session_jwt_as_api_key():
    config.thingsvis_base_url = "http://localhost:8000"
    config.profiles = {"tenant_admin": {"thingsvis_token": "session-jwt"}}
    client = ThingsPanelClient(transport=httpx.MockTransport(lambda request: httpx.Response(200)))
    with pytest.raises(KeyError, match="缺少 ThingsVis Dashboard Open API Key"):
        asyncio.run(client.request_api("thingsvis", "GET", "/api/open/v1/dashboards", profile="tenant_admin"))
