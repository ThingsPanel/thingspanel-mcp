#!/usr/bin/env python3
"""Build the checked-in API inventory from ThingsPanel and ThingsVis source trees."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any

HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"}
DOC_METHODS = {method.lower() for method in HTTP_METHODS}


def canonical(path: str) -> str:
    return re.sub(r"\{([^}]+)\}", r":\1", path)


def tool_name(service: str, method: str, path: str, used: set[str]) -> str:
    prefix = "tp" if service == "thingspanel" else "tv"
    core = canonical(path)
    if core.startswith("/api/v1/"):
        core = core[len("/api/v1"):]
    parts = []
    for segment in core.split("/"):
        if not segment:
            continue
        if segment.startswith(":"):
            parts.append("by_" + segment[1:])
        elif segment.startswith("*"):
            parts.append("all_" + segment[1:])
        else:
            parts.append(re.sub(r"[^a-zA-Z0-9]+", "_", segment).strip("_").lower())
    candidate = re.sub(r"_+", "_", f"{prefix}_{method.lower()}_{'_'.join(parts)}").strip("_")
    if len(candidate) > 62:
        suffix = hashlib.sha1(candidate.encode()).hexdigest()[:8]
        candidate = candidate[:53].rstrip("_") + "_" + suffix
    if candidate in used:
        suffix = hashlib.sha1((service + method + path).encode()).hexdigest()[:8]
        candidate = candidate[:53].rstrip("_") + "_" + suffix
    used.add(candidate)
    return candidate


def load_swagger(path: Path) -> dict[tuple[str, str], str]:
    spec = json.loads(path.read_text())
    records: dict[tuple[str, str], str] = {}
    for route, path_item in spec.get("paths", {}).items():
        for method, operation in path_item.items():
            if method.lower() in DOC_METHODS:
                records[(method.upper(), canonical(route))] = operation.get("summary") or operation.get("operationId") or ""
    return records


def thingsvis_routes(root: Path) -> list[dict[str, Any]]:
    api_root = root / "apps/server/src/app/api"
    records = []
    for file in sorted(api_root.rglob("route.ts")):
        rel = file.relative_to(api_root).as_posix()
        text = file.read_text(errors="ignore")
        methods = re.findall(r"export\s+(?:async\s+)?function\s+(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD)\b", text)
        for method in methods:
            if method == "OPTIONS" or (rel == "v1/health/route.ts" and method != "GET"):
                continue
            route = "/api/" + rel.removesuffix("/route.ts")
            route = route.replace("[...filename]", "*filename")
            route = re.sub(r"\[([^\]]+)\]", r":\1", route)
            records.append({"service": "thingsvis", "method": method, "path": route, "source": f"{rel}"})
    return records


def classify(service: str, method: str, route: str) -> tuple[str, bool, str]:
    if service == "thingspanel":
        public = route in {"/health"} or route.startswith((
            "/api/v1/login", "/api/v1/verification", "/api/v1/reset/password",
            "/api/v1/tenant/email/register", "/api/v1/tenant/has-admin",
            "/api/v1/tenant/setup-state", "/api/v1/tenant/super-admin/init",
            "/api/v1/tenant/market-register", "/api/v1/device/auth", "/api/v1/plugin/",
            "/api/v1/device/gateway-register", "/api/v1/device/gateway-sub-register",
        ))
        security = "public_or_device_plugin_auth" if public else "thingspanel_jwt_casbin"
        if not route.startswith("/api/v1/") and route != "/health":
            return "infrastructure", False, "Infrastructure route; excluded from business tools."
        return security, True, "Writes and commands require explicit caller intent; backend RBAC remains authoritative."

    if route.startswith("/api/internal/"):
        return "thingsvis_internal_secret", True, "Requires the configured ThingsVis internal service token; server validates x-internal-token."
    if route.startswith("/api/v1/public/") or route == "/api/v1/health":
        return "thingsvis_public", True, "Public ThingsVis route; expose only the documented public behavior."
    if route.startswith("/api/v1/auth/"):
        if route.endswith("/sso"):
            return "thingsvis_sso_verified", True, "Requires a ThingsPanel JWT in the selected profile; ThingsVis verifies it server-to-server and derives identity/role from backend response."
        return "thingsvis_auth", True, "Authentication endpoint; no existing account token required."
    if route.startswith("/api/open/v1/apps"):
        return "thingsvis_bearer", True, "App and API-key management is scoped to the authenticated ThingsVis session user."
    if route.startswith("/api/open/v1/dashboards"):
        return "thingsvis_open_api_key", True, "Requires ThingsVis Open API key semantics."
    return "thingsvis_bearer", True, "Requires a ThingsVis Bearer token with server-enforced role and tenant scope."


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend-root", type=Path, required=True)
    parser.add_argument("--thingsvis-root", type=Path, required=True)
    parser.add_argument("--swagger", type=Path)
    parser.add_argument("--output", type=Path, default=Path("src/thingspanel_mcp/api_manifest.json"))
    args = parser.parse_args()
    swagger_path = args.swagger or args.backend_root / "docs/swagger.json"
    doc_ops = load_swagger(swagger_path)

    proc = subprocess.run(
        ["go", "run", str(Path(__file__).with_name("route_inventory.go")), str(args.backend_root)],
        check=True, capture_output=True, text=True,
    )
    backend_routes = json.loads(proc.stdout)
    records: dict[tuple[str, str, str], dict[str, Any]] = {}
    for item in backend_routes:
        route = item["path"]
        method = item["method"]
        key = ("thingspanel", method, route)
        if key not in records:
            security, enabled, note = classify("thingspanel", method, route)
            summary = doc_ops.get((method, canonical(route)), "")
            records[key] = {
                "service": "thingspanel", "method": method, "path": route,
                "summary": summary or f"ThingsPanel API {method} {route}",
                "source": f"{Path(item['file']).relative_to(args.backend_root).as_posix()}:{item['line']}",
                "security": security, "enabled": enabled, "notes": note,
            }
    for item in thingsvis_routes(args.thingsvis_root):
        key = (item["service"], item["method"], item["path"])
        if key not in records:
            security, enabled, note = classify("thingsvis", item["method"], item["path"])
            records[key] = {
                **item, "summary": f"ThingsVis API {item['method']} {item['path']}",
                "security": security, "enabled": enabled, "notes": note,
            }

    used: set[str] = set()
    operations = []
    for key, record in sorted(records.items()):
        record["tool_name"] = tool_name(record["service"], record["method"], record["path"], used)
        record["path_parameters"] = re.findall(r"[:*]([A-Za-z0-9_]+)", record["path"])
        record["stream"] = (
            "websocket" if record["path"].endswith("/ws") or "/ws/" in record["path"]
            else "sse" if record["service"] == "thingspanel" and record["path"] == "/api/v1/events" and record["method"] == "GET"
            else None
        )
        record["destructive"] = record["method"] in {"POST", "PUT", "PATCH", "DELETE"}
        operations.append(record)
    output = {"schema_version": 1, "source_counts": {
        "thingspanel_registrations": len(backend_routes),
        "thingspanel_unique": len([x for x in operations if x["service"] == "thingspanel"]),
        "swagger_operations": len(doc_ops),
        "thingsvis_operations": len([x for x in operations if x["service"] == "thingsvis"]),
    }, "operations": operations}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(output["source_counts"], ensure_ascii=False))
    print(f"enabled={sum(op['enabled'] for op in operations)} tools; disabled={sum(not op['enabled'] for op in operations)} audited routes")


if __name__ == "__main__":
    main()
