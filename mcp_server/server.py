# mcp_server/server.py

import os
import logging
import uvicorn
from starlette.requests import Request
from starlette.responses import JSONResponse
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from tools.kg_query import register_kg_query_tool
from tools.status_code_lookup import (
    register_status_code_lookup_tool,
)

logging.basicConfig(level=logging.INFO)

# Create one MCP server for both tools.
# mcp = FastMCP("Surface Sterling OMS")
# Hostname Render assigns to your service
ALLOWED_HOST = os.getenv("MCP_ALLOWED_HOST", "surface-mcp-server.onrender.com")

mcp = FastMCP(
    "Surface Sterling OMS",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[
            ALLOWED_HOST,
            f"{ALLOWED_HOST}:*",
            "localhost:*",
            "127.0.0.1:*",
        ],
        allowed_origins=[
            f"https://{ALLOWED_HOST}",
            "http://localhost:*",
            "http://127.0.0.1:*",
        ],
    ),
)

@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request):
    return JSONResponse({"status": "ok"})

# Register Knowledge Graph query tool.
register_kg_query_tool(mcp)

# Register status code lookup tool.
register_status_code_lookup_tool(mcp)

# Expose the Streamable HTTP MCP application.

app = mcp.streamable_http_app()


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("MCP_HOST", "0.0.0.0"),
        port=int(os.getenv("MCP_PORT", "8001")),
        log_level="info",
    )




 
