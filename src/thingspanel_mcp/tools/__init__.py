from mcp.server import FastMCP

from . import device, product, data, alarm
from ..settings import thingspanel_settings


def add_tools(mcp: FastMCP):
    """
    Add all enabled tools to the MCP server.
    """
    if thingspanel_settings.tools.device.enabled:
        device.add_tools(mcp)
    if thingspanel_settings.tools.product.enabled:
        product.add_tools(mcp)
    if thingspanel_settings.tools.data.enabled:
        data.add_tools(mcp)
    if thingspanel_settings.tools.alarm.enabled:
        alarm.add_tools(mcp) 