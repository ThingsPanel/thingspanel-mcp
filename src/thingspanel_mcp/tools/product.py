"""
Product management tools for ThingsPanel.
"""

import json
from typing import Any, Dict, List, Optional

from mcp.server import FastMCP
from pydantic import BaseModel, Field

from ..client import ThingsPanelClient
from ..settings import thingspanel_settings


class ProductListRequest(BaseModel):
    """Arguments for listing products."""
    limit: Optional[int] = Field(
        default=10, description="Maximum number of products to return"
    )
    offset: Optional[int] = Field(
        default=0, description="Offset for pagination"
    )
    name: Optional[str] = Field(
        default=None, description="Filter by product name"
    )


async def list_products(arguments: ProductListRequest) -> bytes:
    """List products from ThingsPanel."""
    client = ThingsPanelClient(
        thingspanel_settings.url,
        thingspanel_settings.api_key,
    )
    params = arguments.model_dump(exclude_none=True)
    result = await client.list_products(params)
    return json.dumps(result).encode()


def add_tools(mcp: FastMCP):
    """Add product management tools to the MCP server."""
    mcp.add_tool(list_products) 