"""Day 3 IN03: a real MCP server (FastMCP) exposing Walmart live-data tools.

Mirrors the FastMCP section of
`Day3/IN03_API_MCP_Frameworks_Build_vs_Buy - Intro.ipynb`: the server owns the
tool schema; any MCP client discovers and calls the tools without the developer
writing tool descriptions in a prompt.

Run standalone (stdio transport):

    source ./activate
    python -m day3.lab.mcp_server

Or let `python -m day3.lab.rest_mcp` launch and connect to it automatically.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from day3.lab.live_api import get_store_weather, search_demand_trends

mcp = FastMCP("walmart-retail")


@mcp.tool()
def store_weather(city: str, country_code: str = "IN") -> dict:
    """Get real-time weather at a Walmart store city. Rain drives umbrella and
    raincoat sales; heat drives cold beverages; cold drives hot beverages."""
    return get_store_weather(city, country_code)


@mcp.tool()
def demand_trends(query: str, max_results: int = 3) -> dict:
    """Search real-time retail product demand trends and market signals."""
    return search_demand_trends(query, max_results)


if __name__ == "__main__":
    mcp.run()
