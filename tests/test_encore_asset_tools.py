import asyncio
import hashlib
import os

import httpx
from mcp.server.fastmcp import FastMCP

from thingspanel_mcp.encore_asset_tools import EncoreAssetClient, register_encore_asset_tools, UPLOAD_LIMIT


class Config:
    encore_base_url = "http://127.0.0.1:8899"
    def get_profile(self, profile):
        if profile != "default": raise KeyError(profile)
        return {"thingspanel_token": "secret-fixture-token"}


def tools(handler, config=None):
    client = EncoreAssetClient(transport=httpx.MockTransport(handler), config_obj=config or Config())
    server = FastMCP("asset-test")
    assert register_encore_asset_tools(server, client) == 2
    return server._tool_manager


def call(manager, name, kwargs):
    return asyncio.run(manager.call_tool(name, kwargs))


def test_upload_requires_confirmation_and_uses_exact_contract(tmp_path):
    path = tmp_path / "image.png"
    path.write_bytes(b"test-image")
    calls = []
    def handler(req):
        calls.append(req)
        body = req.read()
        assert req.url.path == "/api/v2/file-assets"
        assert req.headers["authorization"] == "Bearer secret-fixture-token"
        assert req.headers["idempotency-key"] == "upload-key-1"
        assert b'name="purpose"' in body and b'template-image' in body
        assert b'name="file"' in body and b'test-image' in body
        return httpx.Response(201, json={"data": {"assetId": "a1"}})
    manager = tools(handler)
    args = {"file_path": str(path), "idempotency_key": "upload-key-1"}
    assert call(manager, "encore_upload_template_image", args)["confirmation_required"]
    assert calls == []
    args["confirmed"] = True
    result = call(manager, "encore_upload_template_image", args)
    assert result["ok"] and result["data"]["data"]["assetId"] == "a1"
    assert len(calls) == 1


def test_upload_rejects_invalid_key_oversize_and_remote_http(tmp_path):
    path = tmp_path / "big"
    with path.open("wb") as f: f.truncate(UPLOAD_LIMIT + 1)
    calls = []
    def handler(req): calls.append(req); return httpx.Response(201, json={})
    manager = tools(handler)
    result = call(manager, "encore_upload_template_image", {"file_path": str(path), "idempotency_key": "bad", "confirmed": True})
    assert result["error"]["type"] == "invalid_idempotency_key"
    result = call(manager, "encore_upload_template_image", {"file_path": str(path), "idempotency_key": "upload-key-1", "confirmed": True})
    assert result["error"]["type"] == "invalid_file"
    remote = Config(); remote.encore_base_url = "http://example.com"
    result = call(tools(handler, remote), "encore_upload_template_image", {"file_path": str(path), "idempotency_key": "upload-key-1", "confirmed": True})
    assert result["error"]["type"] == "configuration"
    assert calls == []


def test_download_stream_checks_hash_and_no_overwrite(tmp_path):
    data = b"abcde" * (2 * 1024 * 1024)  # larger than 8 MiB
    digest = hashlib.sha256(data).hexdigest()
    calls = []
    def handler(req):
        calls.append(req)
        assert req.url.path == "/api/v2/metadata-downloads/id-1"
        return httpx.Response(200, headers={"etag": '"sha256-' + digest + '"'}, content=data)
    target = tmp_path / "result.csv"
    manager = tools(handler)
    args = {"download_id": "id-1", "output_path": str(target)}
    assert call(manager, "encore_download_metadata_artifact", args)["confirmation_required"]
    assert not target.exists() and calls == []
    args["confirmed"] = True
    result = call(manager, "encore_download_metadata_artifact", args)
    assert result["ok"] and result["data"]["bytes"] == len(data)
    assert target.read_bytes() == data
    result = call(manager, "encore_download_metadata_artifact", args)
    assert result["error"]["type"] == "destination_exists" and len(calls) == 1


def test_download_mismatch_or_redirect_leaves_no_file(tmp_path):
    target = tmp_path / "data"
    def mismatch(req): return httpx.Response(200, headers={"etag": '"sha256-' + '0' * 64 + '"'}, content=b"x")
    args = {"download_id": "id-1", "output_path": str(target), "confirmed": True}
    result = call(tools(mismatch), "encore_download_metadata_artifact", args)
    assert result["error"]["type"] == "checksum_mismatch"
    assert list(tmp_path.iterdir()) == []
    def redirect(req): return httpx.Response(302, headers={"location": "https://example.com/steal"})
    result = call(tools(redirect), "encore_download_metadata_artifact", args)
    assert result["error"]["type"] == "http_error"
    assert list(tmp_path.iterdir()) == []


def test_failures_do_not_expose_token_or_raw_transport_errors(tmp_path):
    def handler(req): raise httpx.ConnectError("secret-fixture-token")
    path = tmp_path / "x"
    path.write_bytes(b"test")
    manager = tools(handler)
    result = call(manager, "encore_upload_template_image", {"file_path": str(path), "idempotency_key": "upload-key-1", "confirmed": True})
    assert result["error"]["type"] == "outcome_unknown"
    assert "secret-fixture-token" not in str(result)


def test_download_stream_failure_cleans_temporary_file(tmp_path):
    class BrokenStream(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b"partial"
            raise httpx.ReadError("secret-fixture-token")

    def handler(req):
        return httpx.Response(200, headers={"etag": '"sha256-' + '0' * 64 + '"'}, stream=BrokenStream())
    target = tmp_path / "output"
    result = call(tools(handler), "encore_download_metadata_artifact", {"download_id": "d1", "output_path": str(target), "confirmed": True})
    assert result["error"]["type"] == "download_failed"
    assert "secret-fixture-token" not in str(result)
    assert list(tmp_path.iterdir()) == []


def test_download_concurrent_target_creation_never_overwrites(tmp_path):
    target = tmp_path / "output"
    payload = b"verified"
    digest = hashlib.sha256(payload).hexdigest()

    class RaceStream(httpx.AsyncByteStream):
        async def __aiter__(self):
            target.write_bytes(b"other process")
            yield payload

    def handler(req):
        return httpx.Response(200, headers={"etag": '"sha256-' + digest + '"'}, stream=RaceStream())
    result = call(tools(handler), "encore_download_metadata_artifact", {"download_id": "d1", "output_path": str(target), "confirmed": True})
    assert result["error"]["type"] == "destination_exists"
    assert target.read_bytes() == b"other process"
    assert len(list(tmp_path.iterdir())) == 1
