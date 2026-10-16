# mcp_server/server.py

import os
import logging
import uvicorn

from mcp.server.fastmcp import FastMCP

from tools.kg_query import register_kg_query_tool
from tools.status_code_lookup import (
    register_status_code_lookup_tool,
)

logging.basicConfig(level=logging.INFO)

# Create one MCP server for both tools.
mcp = FastMCP("Surface Sterling OMS")

# Register Knowledge Graph query tool.
register_kg_query_tool(mcp)

# Register status code lookup tool.
register_status_code_lookup_tool(mcp)

# Expose the Streamable HTTP MCP application.
from mcp.server.transport_security import TransportSecuritySettings

app = mcp.streamable_http_app(
    transport_security=TransportSecuritySettings(
        allowed_hosts=[
            "surface-mcp-server.onrender.com",
            "surface-mcp-server.onrender.com:*",
        ]
    )
)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("MCP_HOST", "0.0.0.0"),
        port=int(os.getenv("MCP_PORT", "8001")),
        log_level="info",
    )
 
