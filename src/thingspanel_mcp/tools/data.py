"""
Data retrieval tools for ThingsPanel.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from mcp.server import FastMCP
from pydantic import BaseModel, Field

from ..client import ThingsPanelClient
from ..settings import thingspanel_settings


class DeviceDataRequest(BaseModel):
    """Arguments for querying device data."""
    device_id: str = Field(
        description="Unique identifier for the device"
    )
    start_time: Optional[datetime] = Field(
        default=None, description="Start time for data query (ISO format)"
    )
    end_time: Optional[datetime] = Field(
        default=None, description="End time for data query (ISO format)"
    )
    limit: Optional[int] = Field(
        default=100, description="Maximum number of data points to return"
    )
    attributes: Optional[List[str]] = Field(
        default=None, description="List of specific attributes to retrieve"
    )


async def get_device_data(arguments: DeviceDataRequest) -> bytes:
    """Get historical data for a device from ThingsPanel."""
    client = ThingsPanelClient(
        thingspanel_settings.url,
        thingspanel_settings.api_key,
    )
    
    params = {}
    if arguments.start_time:
        params["start_time"] = arguments.start_time.isoformat()
    if arguments.end_time:
        params["end_time"] = arguments.end_time.isoformat()
    if arguments.limit:
        params["limit"] = arguments.limit
    if arguments.attributes:
        params["attributes"] = ",".join(arguments.attributes)
    
    result = await client.get_device_data(arguments.device_id, params)
    return json.dumps(result).encode()


def add_tools(mcp: FastMCP):
    """Add data retrieval tools to the MCP server."""
    mcp.add_tool(get_device_data) 