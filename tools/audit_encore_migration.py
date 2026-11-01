#!/usr/bin/env python3
"""Read-only inventory/comparison of Encore API declarations and MCP manifest."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

DECL = re.compile(r"^\s*//encore:api\s+(?P<attrs>.+)$", re.M)
ATTR = re.compile(r"(\w+)=([^\s]+)")
WRITE = {"POST", "PUT", "PATCH", "DELETE"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True, help="固定版本的 Community 源码目录")
    ap.add_argument("--manifest", type=Path, default=Path("src/thingspanel_mcp/encore_manifest.json"))
    ap.add_argument("--output", type=Path, default=Path("docs/encore-migration-audit.md"))
    a = ap.parse_args()
    root = a.source.resolve()
    if not (root / "encore-api").is_dir():
        ap.error("--source 必须包含 encore-api 目录")
    rows = []
    for f in sorted((root / "encore-api").rglob("*.go")):
        content = f.read_text(errors="replace")
        for m in DECL.finditer(content):
            attrs = dict(ATTR.findall(m.group("attrs")))
            if "method" not in attrs or "path" not in attrs:
                continue
            path = attrs["path"]
            words = set(m.group("attrs").split())
            security = "public_declaration" if "public" in words else "authenticated" if "auth" in words else "private_or_unknown"
            for method in attrs["method"].upper().split(","):
                risk = "write_unconfirmed" if method in WRITE else "read"
                rows.append({"method": method, "path": path, "security": security, "risk": risk,
                             "source": f.as_posix().replace(root.as_posix()+"/", "")})
    manifest = json.loads(a.manifest.read_text())
    existing = {(x["method"].upper(), x["path"].replace(":", ":")) for x in manifest.get("operations", [])}
    for row in rows:
        row["manifest_match"] = (row["method"], row["path"]) in existing
        row["migration"] = "review_only_unconfirmed" if row["risk"] == "write_unconfirmed" else "review_required"
    rows.sort(key=lambda x: (x["security"], x["method"], x["path"]))
    counts = Counter((r["security"], r["risk"], r["manifest_match"]) for r in rows)
    lines = ["# Encore API migration audit", "", f"Source: `{root}` (Encore declarations under `encore-api/`).", f"Compared with `{a.manifest}`.",
             "", "This is an inventory aid, not an exposure allow-list. Matches compare literal declaration paths only, including disabled entries; wildcard raw handlers and dedicated upload/download tools are not expanded. An unmatched path is not proof that an operation is unavailable. A public declaration may enforce authorization inside a raw handler. Verify source version, handler authorization, deployment routing and every method before enabling a tool.", "",
             f"Declared operations: **{len(rows)}**; manifest matches: **{sum(r['manifest_match'] for r in rows)}**; unmatched: **{sum(not r['manifest_match'] for r in rows)}**.", "",
             "## Counts", "", "| Visibility | Operation class | Manifest match | Count |", "|---|---|---:|---:|"]
    for (vis, risk, matched), n in sorted(counts.items()):
        lines.append(f"| {vis} | {risk} | {'yes' if matched else 'no'} | {n} |")
    lines += ["", "## Per-operation inventory", "", "| Method | Path | Visibility | Safety | Manifest | Migration disposition | Source |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['method']} | `{r['path']}` | {r['security']} | {r['risk']} | {'match' if r['manifest_match'] else 'no'} | {r['migration']} | `{r['source']}` |")
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text("\n".join(lines)+"\n")
    print(f"wrote {a.output}: {len(rows)} operations, {sum(r['manifest_match'] for r in rows)} matches")


if __name__ == "__main__":
    main()
