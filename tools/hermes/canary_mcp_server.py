"""Inert CPW-owned MCP proof: one deterministic tool, no external effects."""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("cpw-canary", host="0.0.0.0", port=8766,
              stateless_http=True, json_response=True, streamable_http_path="/mcp")


@mcp.tool()
def canary_ping() -> dict[str, str]:
    """Return an inert deterministic non-authoritative canary response."""
    return {"canary": "cpw-canary", "version": "1.0.0", "status": "ok"}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
