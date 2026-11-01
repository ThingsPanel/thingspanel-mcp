# ThingsPanel MCP: Encore migration development build

Requires Python 3.10 or newer.

This branch is an unreleased `0.2.0.dev0` candidate. It registers source-verified Encore tools; the 0.1.11 legacy route tools are not registered by default. See [migration tasks](ENCORE_MIGRATION_TASKS.md) for development and test status, and [中文说明](README_CN.md) for detailed usage.

```bash
python3 -m pip install -e .
export THINGSPANEL_ENCORE_BASE_URL=https://your-thingspanel-entry
export THINGSPANEL_TOKEN='<user-token>'
thingspanel-mcp --transport stdio
```

Configure the Encore base URL explicitly. HTTPS is required except on loopback. Supply credentials securely and keep stdout reserved for the MCP protocol. The default tool list targets Community main `7f694779`. Native device metadata tools require a deployment compatible with candidate `d4e0540b` and explicit `THINGSPANEL_ENABLE_NATIVE_METADATA=1`; enabling tools does not deploy the backend or fall back to legacy APIs.

Northbound tools are also disabled by default. Enable `THINGSPANEL_ENABLE_NORTHBOUND=1` only after the Northbound service has actually been built and deployed.

Writes require `confirmed=true` and, where specified, an explicit idempotency key or strong ETag. A timed-out write has an unknown outcome: check its status first and retry with the same key only where the server guarantees idempotency. Do not log sensitive responses.

The `confirmed` argument alone is not evidence of human approval; the MCP host must obtain the user's confirmation. Sensitive responses are returned to the authorized caller and should not be logged or cached by the host.

Run `python3 -m pytest -q` for local tests. Real service, release and device acceptance are tracked separately in the task list.
