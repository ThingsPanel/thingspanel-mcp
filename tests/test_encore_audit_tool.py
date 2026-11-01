import json
import subprocess
import sys
from pathlib import Path


def test_audit_splits_methods_and_labels_public_declarations(tmp_path):
    root = tmp_path / "source"
    folder = root / "encore-api" / "example"
    folder.mkdir(parents=True)
    (folder / "api.go").write_text("//encore:api public raw method=GET,POST path=/v1/fixture\n//encore:api auth method=GET path=/v1/auth\n", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"operations": [{"method": "GET", "path": "/v1/fixture"}]}))
    output = tmp_path / "audit.md"
    script = Path(__file__).parents[1] / "tools" / "audit_encore_migration.py"
    subprocess.run([sys.executable, str(script), "--source", str(root), "--manifest", str(manifest), "--output", str(output)], check=True)
    report = output.read_text(encoding="utf-8")
    assert "Declared operations: **3**" in report
    assert "| GET | `/v1/fixture` | public_declaration | read | match |" in report
    assert "| POST | `/v1/fixture` | public_declaration | write_unconfirmed | no |" in report
    assert "| GET | `/v1/auth` | authenticated | read | no |" in report
