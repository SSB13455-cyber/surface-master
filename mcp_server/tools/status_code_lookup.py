import logging
from typing import Any

from mcp.server.fastmcp import FastMCP
from kg_layer import Neo4JClient

logger = logging.getLogger(__name__)


def register_status_code_lookup_tool(mcp: FastMCP) -> None:
    """Register the Sterling OMS status-code lookup tool."""

    @mcp.tool()
    def lookup_status_code(status_name: str) -> dict[str, Any]:
        """
        Resolve a Sterling OMS status name or description
        to its verified numeric status code.

        Use this tool when an OMS API requires a numeric
        status code. Do not guess status codes.

        Args:
            status_name: Status name or description,
                for example "Shipped".

        Returns:
            The matching status code and status metadata,
            or an error if no match is found.
        """
        client = None

        try:
            client = Neo4JClient()

            cypher = """
            MATCH (sc:StatusCode)
            WHERE sc.name CONTAINS $status_name
               OR sc.description CONTAINS $status_name
            RETURN sc.code, sc.name, sc.description, sc.process_type
            LIMIT 5
            """

            results = client.run_query(
                cypher,
                {"status_name": status_name}
            )

            if not results:
                return {
                    "success": False,
                    "status_name": status_name,
                    "status_code": None,
                    "message": (
                        "No matching status was found "
                        "in the Knowledge Graph."
                    )
                }

            result = results[0]
            status_code = result.get("sc.code")

            return {
                "success": True,
                "status_name": status_name,
                "status_code": status_code,
                "found_as": {
                    "name": result.get("sc.name"),
                    "description": result.get("sc.description"),
                    "process_type": result.get("sc.process_type")
                }
            }

        except Exception:
            logger.exception("Status code lookup failed")
            return {
                "success": False,
                "status_name": status_name,
                "status_code": None,
                "error": "Status lookup failed. Check server logs."
            }

        finally:
            if client is not None:
                try:
                    client.close()
                except Exception:
                    logger.exception(
                        "Failed to close Neo4j client"
                    )
