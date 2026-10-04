"""Typed MCP results for the human-friendly ThingsPanel tools."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ToolError(BaseModel):
    code: str
    message: str


class ToolResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    summary: str
    error: Optional[ToolError] = None


class DeviceItem(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    device_number: Optional[str] = None
    device_config_name: Optional[str] = None
    access_way: Optional[str] = None
    is_online: Optional[bool] = None
    activate_flag: Optional[str] = None
    is_enabled: Optional[str] = None
    created_at: Optional[str] = None


class DeviceListData(BaseModel):
    devices: List[DeviceItem]
    total: int
    page: int
    page_size: int


class DeviceListResult(ToolResult):
    data: Optional[DeviceListData] = None


class DeviceConfigInfo(BaseModel):
    name: Optional[str] = None
    device_type: Optional[str] = None
    protocol_type: Optional[str] = None
    voucher_type: Optional[str] = None


class DeviceInfo(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    device_number: Optional[str] = None
    is_online: Optional[bool] = None
    activate_flag: Optional[str] = None
    is_enabled: Optional[str] = None
    access_way: Optional[str] = None
    created_at: Optional[str] = None
    update_at: Optional[str] = None
    device_config: Optional[DeviceConfigInfo] = None


class DeviceDetailData(BaseModel):
    device: DeviceInfo


class DeviceDetailResult(ToolResult):
    data: Optional[DeviceDetailData] = None


class DeviceStatusData(BaseModel):
    device_id: str
    status: Literal["online", "offline", "unknown"]
    is_online: Optional[bool] = None


class DeviceStatusResult(ToolResult):
    data: Optional[DeviceStatusData] = None


class TelemetryItem(BaseModel):
    key: Optional[str] = None
    label: Optional[str] = None
    value: Any = None
    unit: Optional[str] = None
    timestamp: Any = None


class DeviceTelemetryData(BaseModel):
    device_id: str
    items: List[TelemetryItem]


class DeviceTelemetryResult(ToolResult):
    data: Optional[DeviceTelemetryData] = None


class TelemetryByKeyData(BaseModel):
    device_id: str
    key: str
    item: Optional[TelemetryItem] = None


class TelemetryByKeyResult(ToolResult):
    data: Optional[TelemetryByKeyData] = None


class HistoryPoint(BaseModel):
    timestamp: Any = None
    value: Any = None


class TelemetryHistoryData(BaseModel):
    device_id: str
    key: str
    time_range: str
    aggregate_window: str
    aggregate_function: Optional[str] = None
    start: Any = None
    end: Any = None
    total_points: int
    points: List[HistoryPoint]
    truncated: bool


class TelemetryHistoryResult(ToolResult):
    data: Optional[TelemetryHistoryData] = None


class ModelDefinition(BaseModel):
    data_name: Optional[str] = None
    data_identifier: Optional[str] = None
    data_type: Optional[str] = None
    unit: Optional[str] = None
    read_write_flag: Optional[str] = None
    params: List[Dict[str, Any]] = Field(default_factory=list)


class DeviceModelData(BaseModel):
    device_id: str
    device_template_id: Optional[str] = None
    model_type: str
    definitions: Dict[str, List[ModelDefinition]]


class DeviceModelResult(ToolResult):
    data: Optional[DeviceModelData] = None


class OperationData(BaseModel):
    device_id: str
    operation: Literal["telemetry_control", "attribute_set", "command"]
    request: Dict[str, Any]
    accepted: bool
    message_id: Optional[str] = None
    status: Optional[str] = None


class OperationResult(ToolResult):
    data: Optional[OperationData] = None


class CommandStatusData(BaseModel):
    message_id: str
    status: Literal[
        "accepted", "published", "publish_failed", "device_succeeded",
        "device_failed", "timeout", "not_found", "unknown",
    ]
    raw_status: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    response: Any = None


class CommandStatusResult(ToolResult):
    data: Optional[CommandStatusData] = None


class ModelCheckedControlData(BaseModel):
    device_id: str
    command_type: str
    model: DeviceModelData
    operation: Optional[OperationData] = None


class ModelCheckedControlResult(ToolResult):
    data: Optional[ModelCheckedControlData] = None


class TenantSummaryData(BaseModel):
    tenant_id: Optional[str] = None
    device_total: int
    device_online: int
    online_rate: float
    device_active: int
    message_count: int


class TenantSummaryResult(ToolResult):
    data: Optional[TenantSummaryData] = None


class DeviceTrendPoint(BaseModel):
    timestamp: Any = None
    device_total: int
    device_online: int
    device_offline: int
    online_rate: float


class DeviceTrendData(BaseModel):
    points: List[DeviceTrendPoint]


class DeviceTrendResult(ToolResult):
    data: Optional[DeviceTrendData] = None


def make_error(code: Any, message: Any, summary: str) -> ToolError:
    return ToolError(code=str(code or "request_failed"), message=str(message or "请求失败"))
