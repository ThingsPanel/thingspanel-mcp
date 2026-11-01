import asyncio
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def test_real_stdio_server_handshake_and_tool_inventory():
    root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    env.update({"PYTHONPATH": str(root / "src"), "THINGSPANEL_ENCORE_BASE_URL": "http://127.0.0.1:44001", "THINGSPANEL_TOKEN": "fixture-token"})
    env.pop("THINGSPANEL_ENABLE_NATIVE_METADATA", None)
    env.pop("THINGSPANEL_ENABLE_NORTHBOUND", None)
    server = StdioServerParameters(command=sys.executable, args=["-c", "from thingspanel_mcp.main import main; main()"], env=env, cwd=root)
    async def check():
        async with stdio_client(server) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                names = {tool.name for tool in (await session.list_tools()).tools}
                assert "encore_thingmodel_list" in names
                assert "encore_notification_send" in names
                assert "encore_device_list" not in names
                assert "send_device_command" not in names
                assert len(names) > 40
    asyncio.run(check())


def test_stdio_tool_calls_real_local_http_server():
    seen = {}
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            seen["path"] = self.path
            seen["auth"] = self.headers.get("Authorization")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"modelID":"fixture-model"}')
        def log_message(self, *_args):
            pass
    server_http = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server_http.serve_forever, daemon=True)
    thread.start()
    root = Path(__file__).resolve().parents[1]
    env = dict(os.environ, PYTHONPATH=str(root / "src"), THINGSPANEL_ENCORE_BASE_URL=f"http://127.0.0.1:{server_http.server_port}", THINGSPANEL_TOKEN="fixture-token")
    env.pop("THINGSPANEL_ENABLE_NATIVE_METADATA", None)
    env.pop("THINGSPANEL_ENABLE_NORTHBOUND", None)
    server = StdioServerParameters(command=sys.executable, args=["-c", "from thingspanel_mcp.main import main; main()"], env=env, cwd=root)
    async def check():
        async with stdio_client(server) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                result = await session.call_tool("encore_thingmodel_get", {"path_params": {"modelID": "fixture-model"}})
                assert not result.isError and result.structuredContent.get("ok"), result.structuredContent
                assert result.structuredContent["data"]["modelID"] == "fixture-model"
    try:
        asyncio.run(check())
        assert seen == {"path": "/api/v2/thing-models/fixture-model", "auth": "Bearer fixture-token"}
    finally:
        server_http.shutdown()
        server_http.server_close()
        thread.join(timeout=5)
