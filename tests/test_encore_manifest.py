"""Static provenance and safety checks for the Encore operation inventory."""
import json
import re
from pathlib import Path


MANIFEST = Path(__file__).parents[1] / "src" / "thingspanel_mcp" / "encore_manifest.json"


def _operations():
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert document["schema_version"] == 1
    return document["operations"]


def test_unique_explicit_operations_and_source_versions():
    operations = _operations()
    assert len({op["tool_name"] for op in operations}) == len(operations)
    assert len({(op["method"], op["path"]) for op in operations}) == len(operations)
    for op in operations:
        assert op["service"] == "encore"
        assert op["method"] in {"GET", "POST", "PUT", "PATCH", "DELETE"}
        assert op["path"].startswith(("/api/v2/", "/v1/"))
        assert set(op["path_parameters"]) == set(re.findall(r":([A-Za-z][A-Za-z0-9_]*)", op["path"]))
        assert op["source_ref"].startswith(("7f694779", "d4e0540b"))
        assert op["availability"] in {"community_main", "metadata_candidate", "community_optional"}
        assert op["enabled"] == (op["availability"] == "community_main")
        assert not op["destructive"] or op["write"]
        assert op["idempotency_location"] in (None, "header", "body")
        assert op["requires_idempotency"] == (op["idempotency_location"] is not None)
        if op["idempotency_location"] == "body":
            assert op["idempotency_field"] == "request_id"
        if op["requires_if_match"]:
            assert op["availability"] == "metadata_candidate" and op["write"]


def test_no_internal_endpoints_or_unsupported_native_enablement():
    for op in _operations():
        assert "/internal/" not in op["path"]
        assert "notification-ingress" not in op["path"]
        assert "notification-group-projections" not in op["path"]
        if op["availability"] == "metadata_candidate":
            assert not op["enabled"]


def test_automation_idempotency_and_admin_instance_paths():
    operations = {op["tool_name"]: op for op in _operations()}
    assert operations["encore_rule_create"]["idempotency_location"] == "body"
    assert operations["encore_rule_run"]["idempotency_location"] == "body"
    assert operations["encore_rule_enable"]["idempotency_location"] is None
    assert operations["encore_alarm_ack"]["idempotency_location"] is None
    for name in ("encore_notification_instance_create", "encore_notification_instance_update", "encore_notification_instance_validate"):
        assert operations[name]["path"].startswith("/api/v2/platform/notification-tenants/:tenantId/")
    assert operations["encore_thingmodel_update"]["idempotency_location"] == "header"
    assert operations["encore_device_update"]["requires_if_match"]
    assert operations["encore_device_command_send"]["destructive"]


def test_candidate_sensitive_and_non_json_boundaries():
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    operations = {op["tool_name"]: op for op in document["operations"]}
    candidate = [op for op in operations.values() if op["availability"] == "metadata_candidate"]
    assert len(candidate) == 63
    assert operations["encore_device_credentials"]["sensitive_response"]
    assert operations["encore_device_credential_create"]["sensitive_response"]
    assert operations["encore_device_credential_rotate"]["sensitive_response"]
    assert operations["encore_file_asset_get"]["sensitive_response"]
    assert operations["encore_device_bind_template"]["requires_if_match"]
    assert operations["encore_device_gateway_set"]["requires_if_match"]
    assert operations["encore_simulator_profile_update"]["requires_if_match"]
    assert operations["encore_debug_session_stop"]["idempotency_location"] == "header"
    assert operations["encore_simulator_session_close"]["idempotency_location"] is None
    assert not operations["encore_processing_script_test"]["write"]
    excluded = {(op["method"], op["path"]): op for op in document["excluded_operations"]}
    assert excluded[("POST", "/api/v2/file-assets")]["availability"] == "metadata_candidate"
    assert excluded[("GET", "/api/v2/metadata-downloads/:downloadID")]["availability"] == "metadata_candidate"
    assert excluded[("GET", "/api/v2/device-observation-stream")]["availability"] == "not_registered"
    assert all(key not in {(o["method"], o["path"]) for o in operations.values()} for key in excluded)


def test_optional_northbound_and_unsafe_public_routes():
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    operations = {op["tool_name"]: op for op in document["operations"]}
    northbound = [op for op in operations.values() if op["availability"] == "community_optional"]
    assert len(northbound) == 20
    assert all(not op["enabled"] and op["idempotency_location"] is None for op in northbound)
    assert operations["encore_northbound_connection_create"]["sensitive_request"]
    assert operations["encore_northbound_pipeline_test_send"]["destructive"]
    assert operations["encore_northbound_delivery_replay"]["destructive"]
    assert not operations["encore_northbound_pipeline_preview"]["write"]
    assert operations["encore_binding_reconcile"]["destructive"]
    assert operations["encore_automation_events"]["sensitive_response"]
    assert operations["encore_schedule_create"]["idempotency_location"] is None
    excluded = {(op["method"], op["path"]): op for op in document["excluded_operations"]}
    assert excluded[("GET", "/v1/backlog")]["availability"] == "security_review"
    assert excluded[("GET", "/v1/subscriptions")]["availability"] == "service_internal"
    assert excluded[("POST", "/v1/inbox/events")]["availability"] == "service_internal"
