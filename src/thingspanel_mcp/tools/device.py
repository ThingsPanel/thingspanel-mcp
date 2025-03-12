"""
Device management tools for ThingsPanel.
"""

import json
from typing import Any, Dict, List, Optional

from mcp.server import FastMCP
from pydantic import BaseModel, Field

from ..client import ThingsPanelClient
from ..settings import thingspanel_settings


class DeviceListRequest(BaseModel):
    """Arguments for listing devices."""
    limit: Optional[int] = Field(
        default=10, description="Maximum number of devices to return"
    )
    offset: Optional[int] = Field(
        default=0, description="Offset for pagination"
    )
    name: Optional[str] = Field(
        default=None, description="Filter by device name"
    )


class DeviceRequest(BaseModel):
    """Arguments for a device request."""
    device_id: str = Field(
        description="Unique identifier for the device"
    )


class DeviceCreateRequest(BaseModel):
    """Arguments for creating a device."""
    name: str = Field(
        description="The name of the device"
    )
    product_id: str = Field(
        description="The ID of the product this device belongs to"
    )
    description: Optional[str] = Field(
        default=None, description="Description of the device"
    )


class DeviceUpdateRequest(BaseModel):
    """Arguments for updating a device."""
    device_id: str = Field(
        description="Unique identifier for the device"
    )
    name: Optional[str] = Field(
        default=None, description="The name of the device"
    )
    description: Optional[str] = Field(
        default=None, description="Description of the device"
    )


async def list_devices(arguments: DeviceListRequest) -> bytes:
    """List devices from ThingsPanel."""
    client = ThingsPanelClient(
        thingspanel_settings.url,
        thingspanel_settings.api_key,
    )
    params = arguments.model_dump(exclude_none=True)
    result = await client.list_devices(params)
    return json.dumps(result).encode()


async def get_device(arguments: DeviceRequest) -> bytes:
    """Get a device by ID from ThingsPanel."""
    client = ThingsPanelClient(
        thingspanel_settings.url,
        thingspanel_settings.api_key,
    )
    result = await client.get_device(arguments.device_id)
    return json.dumps(result).encode()


async def create_device(arguments: DeviceCreateRequest) -> bytes:
    """Create a new device in ThingsPanel."""
    client = ThingsPanelClient(
        thingspanel_settings.url,
        thingspanel_settings.api_key,
    )
    device_data = arguments.model_dump(exclude_none=True)
    result = await client.create_device(device_data)
    return json.dumps(result).encode()


async def update_device(arguments: DeviceUpdateRequest) -> bytes:
    """Update a device in ThingsPanel."""
    client = ThingsPanelClient(
        thingspanel_settings.url,
        thingspanel_settings.api_key,
    )
    device_id = arguments.device_id
    device_data = arguments.model_dump(exclude={"device_id"}, exclude_none=True)
    result = await client.update_device(device_id, device_data)
    return json.dumps(result).encode()


async def delete_device(arguments: DeviceRequest) -> bytes:
    """Delete a device from ThingsPanel."""
    client = ThingsPanelClient(
        thingspanel_settings.url,
        thingspanel_settings.api_key,
    )
    result = await client.delete_device(arguments.device_id)
    return json.dumps(result).encode()


def add_tools(mcp: FastMCP):
    """Add device management tools to the MCP server."""
    mcp.add_tool(list_devices)
    mcp.add_tool(get_device)
    mcp.add_tool(create_device)
    mcp.add_tool(update_device)
    mcp.add_tool(delete_device) 