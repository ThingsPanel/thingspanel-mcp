import enum

import typer

from . import mcp

app = typer.Typer()


class Transport(enum.StrEnum):
    stdio = "stdio"
    sse = "sse"


@app.command()
def run(transport: Transport = Transport.stdio):
    """Run the ThingsPanel MCP server."""
    mcp.run(transport.value) 