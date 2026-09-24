"""Inventory MCP server (FastMCP).

The Inventory agent is an MCP client that talks to this server. The server owns
the tool schema; the client discovers and calls it (matches the notebook's
"Walmart Inventory MCP Server" example).

Run standalone:

    python -m day3.retail_multi_agent.mcp_inventory_server

Or let `day3.retail_multi_agent.domains` launch it over stdio.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("walmart-inventory", log_level="ERROR")

# SKU -> live stock record (stand-in for a real inventory system).
_INVENTORY = {
    "GV-MILK-1G": "In stock: 24 units | Store 042 Bentonville AR",
    "GV-BREAD-20": "In stock: 61 units | Store 042 Bentonville AR",
    "GV-EGGS-12": "Low stock: 5 units | Store 042 | Restock: Tomorrow",
    "GV-BUTT-1": "In stock: 18 units | Store 042 Bentonville AR",
    "GV-CHKN-3": "Out of stock | Store 042 | Available for online order",
}


@mcp.tool()
def check_inventory(sku: str) -> str:
    """Check live inventory for a product SKU (e.g. GV-MILK-1G)."""
    return _INVENTORY.get(sku.upper(), f"SKU {sku} not found in inventory system")


@mcp.tool()
def low_stock() -> str:
    """List SKUs that are low or out of stock and need attention."""
    flagged = [
        f"{sku}: {status}"
        for sku, status in _INVENTORY.items()
        if "Low stock" in status or "Out of stock" in status
    ]
    return "\n".join(flagged) if flagged else "All tracked SKUs are well stocked."


if __name__ == "__main__":
    mcp.run()
