import asyncio

from mcp.server.fastmcp import FastMCP

from thingspanel_mcp.encore_control_tools import register_encore_control_tools

DEVICE = "514aed98-03ef-4eb8-a01a-cbdc04c3b4ab"
SNAPSHOT = "114aed98-03ef-4eb8-a01a-cbdc04c3b4ab"
EXECUTION = "214aed98-03ef-4eb8-a01a-cbdc04c3b4ab"


class Recorder:
    def __init__(self, result=None):
        self.calls = []
        self.result = result or {"ok": True, "status": 202, "data": {"data": {"id": EXECUTION, "state": "accepted"}}}

    async def request_api(self, **kwargs):
        self.calls.append(kwargs)
        return self.result


def manager(client):
    server = FastMCP("encore-control-test")
    assert register_encore_control_tools(server, client) == 3
    return server._tool_manager


def call(mgr, name, args):
    result = asyncio.run(mgr.call_tool(name, args))
    return result.model_dump() if hasattr(result, "model_dump") else result


def command_args():
    return {"device_id": DEVICE, "identifier": "reboot", "snapshot_id": SNAPSHOT,
            "parameters": {"value": "sensitive-fixture"}, "idempotency_key": "command-key-1"}


def test_submission_requires_confirmation_and_exposes_exact_action():
    client = Recorder()
    out = call(manager(client), "send_native_device_command", command_args())
    assert out["ok"] is False and out["confirmation_required"] is True
    assert out["request_preview"] == {"device_id": DEVICE, "identifier": "reboot", "snapshot_id": SNAPSHOT,
                                      "parameters": {"value": "sensitive-fixture"}, "timeout_seconds": 30,
                                      "delivery_mode": "immediate", "expires_at": None, "label": None}
    assert not client.calls


def test_accepted_command_preserves_receipt_and_exact_request():
    client = Recorder()
    args = command_args(); args["confirmed"] = True
    out = call(manager(client), "send_native_device_command", args)
    assert out["ok"] is True and out["data"]["data"]["state"] == "accepted"
    assert "设备执行结果以回执状态为准" in out["summary"]
    assert len(client.calls) == 1
    req = client.calls[0]
    assert req["service"] == "encore" and req["method"] == "POST"
    assert req["endpoint"] == "/api/v2/devices/:deviceID/command-executions"
    assert req["path_params"] == {"deviceID": DEVICE}
    assert req["idempotency_key"] == "command-key-1" and req["outcome_sensitive"] is True
    assert req["body"] == {"identifier": "reboot", "snapshotId": SNAPSHOT, "parameters": {"value": "sensitive-fixture"}, "timeoutSeconds": 30, "deliveryMode": "immediate"}


def test_unknown_outcome_and_incomplete_response_never_claim_success():
    args = command_args(); args["confirmed"] = True
    for result in ({"ok": False, "error": {"type": "outcome_unknown"}}, {"ok": True, "status": 202, "data": {"data": {"state": "accepted"}}}):
        client = Recorder(result)
        out = call(manager(client), "send_native_device_command", args)
        assert out["ok"] is False and out["error"]["type"] == "outcome_unknown"
        assert len(client.calls) == 1


def test_invalid_key_id_or_mode_never_sends():
    for change in ({"idempotency_key": "bad"}, {"device_id": "../bad"}, {"delivery_mode": "unknown"}, {"timeout_seconds": 301}):
        client = Recorder()
        args = command_args(); args.update(change); args["confirmed"] = True
        out = call(manager(client), "send_native_device_command", args)
        assert out["ok"] is False and not client.calls


def test_receipt_query_and_list_paths_are_native():
    client = Recorder({"ok": True, "status": 200, "data": {"data": {"id": EXECUTION, "state": "unknown"}}})
    mgr = manager(client)
    out = call(mgr, "get_native_command_receipt", {"device_id": DEVICE, "execution_id": EXECUTION})
    assert out["ok"] is True and out["data"]["data"]["state"] == "unknown"
    assert client.calls[-1]["endpoint"] == "/api/v2/devices/:deviceID/command-executions/:executionID"
    assert client.calls[-1]["path_params"] == {"deviceID": DEVICE, "executionID": EXECUTION}
    out = call(mgr, "list_native_command_receipts", {"device_id": DEVICE, "page": 2, "page_size": 10, "identifier": "reboot"})
    assert out["ok"] is True
    assert client.calls[-1]["query"] == {"page": 2, "pageSize": 10, "identifier": "reboot"}
    assert all(req["service"] == "encore" and req["method"] == "GET" for req in client.calls)
