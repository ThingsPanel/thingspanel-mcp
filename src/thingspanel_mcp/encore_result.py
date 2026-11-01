"""Stable object-shaped output for Encore MCP tools."""
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class EncoreToolResult(BaseModel):
    model_config = ConfigDict(extra="allow")
    ok: bool
    summary: Optional[str] = None
    status: Optional[int] = None
    data: Any = None
    error: Any = None
    etag: Optional[str] = None
    confirmation_required: Optional[bool] = None
    request_preview: Any = None
