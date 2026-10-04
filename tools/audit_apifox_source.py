#!/usr/bin/env python3
"""Compare published Apifox API pages with the current ThingsPanel router manifest."""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

BASE_URL = "https://s.apifox.cn/87a62ec6-68e5-4590-ac53-8cfe8a8e814b/"
OPERATION_RE = re.compile(r"^    (get|post|put|patch|delete|head):\s*$")
PATH_RE = re.compile(r"^  (/[^:\n]+):\s*$")


def fetch(url: str) -> Tuple[str, Set[Tuple[str, str]], Optional[str]]:
    request = urllib.request.Request(url, headers={"User-Agent": "thingspanel-mcp-api-audit/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            lines = response.read().decode("utf-8", "replace").splitlines()
    except Exception as exc:  # Do not include request data or credentials in an error.
        return url, set(), type(exc).__name__

    operations: Set[Tuple[str, str]] = set()
    for index, line in enumerate(lines):
        path_match = PATH_RE.match(line)
        if not path_match:
            continue
        path = re.sub(r"\{([^}]+)\}", r":\1", path_match.group(1))
        cursor = index + 1
        while cursor < len(lines) and not PATH_RE.match(lines[cursor]):
            method_match = OPERATION_RE.match(lines[cursor])
            if method_match:
                operations.add((method_match.group(1).upper(), path))
            cursor += 1
    return url, operations, None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("src/thingspanel_mcp/api_manifest.json"))
    parser.add_argument("--output", type=Path, default=Path("docs/apifox-source-diff.md"))
    args = parser.parse_args()

    request = urllib.request.Request(BASE_URL + "llms.txt", headers={"User-Agent": "thingspanel-mcp-api-audit/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        index_text = response.read().decode("utf-8", "replace")
    urls = sorted(set(re.findall(
        r"https://s\.apifox\.cn/87a62ec6-68e5-4590-ac53-8cfe8a8e814b/[^)\s]+\.md",
        index_text,
    )))
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(fetch, urls))

    failures = [(url, error) for url, _, error in results if error]
    if failures:
        raise RuntimeError(f"Apifox pages failed to fetch: {len(failures)}")

    apifox: Set[Tuple[str, str]] = set()
    for _, operations, _ in results:
        apifox.update(operations)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    router = {
        (operation["method"], operation["path"])
        for operation in manifest["operations"]
        if operation["service"] == "thingspanel"
    }
    shared = apifox & router
    apifox_only = sorted(apifox - router)
    router_only = sorted(router - apifox)

    lines = [
        "# Apifox 与当前 ThingsPanel router 差异",
        "",
        f"> 基于 [Apifox llms.txt]({BASE_URL}llms.txt) 及其 {len(urls)} 个 API 页面在线快照生成；method/path 与工作区 backend router AST 清单精确对比。Apifox 页面仅作比对，工具来源仍以当前 router 为准。",
        "",
        "## 计数",
        "",
        f"- Apifox API 页面：{len(urls)}",
        f"- Apifox 唯一 method/path：{len(apifox)}",
        f"- 当前 router 唯一 method/path：{len(router)}",
        f"- 精确匹配：{len(shared)}",
        f"- 仅在 Apifox：{len(apifox_only)}（须确认已删除、未注册或由外部服务提供）",
        f"- 仅在当前 router：{len(router_only)}（源码新接口或文档缺失）",
        "",
        "## 仅在 Apifox",
        "",
        "这些操作没有当前 backend router 注册证据，因此不生成 ThingsPanel MCP 工具。",
        "",
        "| 方法 | Apifox 路径 |",
        "|---|---|",
    ]
    lines.extend(f"| `{method}` | `{path}` |" for method, path in apifox_only)
    lines.extend(["", "## 仅在当前 router", "", "| 方法 | 当前源码路径 |", "|---|---|"])
    lines.extend(f"| `{method}` | `{path}` |" for method, path in router_only)
    lines.append("")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "apifox_pages": len(urls), "apifox_unique": len(apifox),
        "router_unique": len(router), "overlap": len(shared),
        "apifox_only": len(apifox_only), "router_only": len(router_only),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
