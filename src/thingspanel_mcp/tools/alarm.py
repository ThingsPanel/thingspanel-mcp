"""
Alarm management tools for ThingsPanel.
"""

import json
from typing import Any, Dict, List, Optional

from mcp.server import FastMCP
from pydantic import BaseModel, Field

from ..client import ThingsPanelClient
from ..settings import thingspanel_settings


class AlarmListRequest(BaseModel):
    """Arguments for listing alarms."""
    limit: Optional[int] = Field(
        default=10, description="Maximum number of alarms to return"
    )
    offset: Optional[int] = Field(
        default=0, description="Offset for pagination"
    )
    device_id: Optional[str] = Field(
        default=None, description="Filter by device ID"
    )
    status: Optional[str] = Field(
        default=None, description="Filter by alarm status"
    )


async def list_alarms(arguments: AlarmListRequest) -> bytes:
    """List alarms from ThingsPanel."""
    client = ThingsPanelClient(
        thingspanel_settings.url,
        thingspanel_settings.api_key,
    )
    # Note: This is a placeholder as we don't have a specific alarms API defined yet
    # In a real implementation, you would call the appropriate API endpoint
    params = arguments.model_dump(exclude_none=True)
    # For now, we'll return a mock response
    mock_result = {
        "code": 200,
        "data": {
            "list": [
                {
                    "alarm_id": "alarm1",
                    "device_id": "device1",
                    "message": "Temperature too high",
                    "severity": "high",
                    "timestamp": "2023-01-01T12:00:00Z",
                    "status": "active"
                }
            ],
            "total": 1
        },
        "msg": "success"
    }
    return json.dumps(mock_result).encode()


def add_tools(mcp: FastMCP):
    """Add alarm management tools to the MCP server."""
    mcp.add_tool(list_alarms) 