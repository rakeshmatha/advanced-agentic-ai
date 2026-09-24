"""Retail domains: four capabilities, four different integrations.

- Product  -> REST  (internal Product Service)
- Orders   -> REST  (internal Orders Service)
- Inventory-> MCP   (Inventory MCP server via stdio)
- Policy   -> RAG   (FAISS over docs/)

Each capability is exposed as a LangChain tool so any agent can call it.
Python is the glue that binds these different integration styles together.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from common.config import settings

DOCS_DIR = Path(__file__).resolve().parent / "docs"

# --- REST integration: internal microservices (mock data stands in for HTTP) --
_PRODUCT_SERVICE = {
    "milk": {"name": "Great Value Whole Milk 1gal", "price": 3.98, "aisle": 12, "sku": "GV-MILK-1G"},
    "bread": {"name": "Great Value White Bread 20oz", "price": 1.28, "aisle": 8, "sku": "GV-BREAD-20"},
    "eggs": {"name": "Great Value Large Eggs 12ct", "price": 2.68, "aisle": 11, "sku": "GV-EGGS-12"},
    "butter": {"name": "Great Value Unsalted Butter 1lb", "price": 4.48, "aisle": 12, "sku": "GV-BUTT-1"},
    "chicken": {"name": "Great Value Chicken Breast 3lb", "price": 8.97, "aisle": 4, "sku": "GV-CHKN-3"},
}

_ORDER_SERVICE = {
    "WM-2024-001": "Delivered June 28 2026 | 3 items | Total: $24.73",
    "WM-2024-002": "Out for delivery | ETA: Today by 8pm",
    "WM-2024-003": "Processing | Payment confirmed | Ships within 24 hours",
    "WM-2024-004": "Cancelled | Refund of $18.45 issued June 27 2026",
}


def _rest_get(service: str, key: str) -> dict:
    """Simulate an authenticated REST GET to an internal Walmart microservice."""
    if service == "product":
        record = _PRODUCT_SERVICE.get(key.lower())
    else:
        record = _ORDER_SERVICE.get(key.upper())
    if record is None:
        return {"status": 404, "error": f"{service} record not found for '{key}'"}
    return {"status": 200, "service": f"{service}-service", "data": record}


@tool
def product_search(product_name: str) -> str:
    """[REST] Look up a product's price, aisle, and SKU from the Product Service.

    Accepts a plain product name such as 'milk' or 'chicken'.
    """
    lowered = product_name.lower()
    for name in _PRODUCT_SERVICE:
        if name in lowered:
            return json.dumps(_rest_get("product", name))
    return json.dumps(
        {"status": 404, "error": f"no product match for '{product_name}'",
         "available": list(_PRODUCT_SERVICE)}
    )


@tool
def order_status(order_id: str) -> str:
    """[REST] Get an order's status from the Orders Service by id (e.g. WM-2024-002)."""
    return json.dumps(_rest_get("orders", order_id))


# --- MCP integration: Inventory agent is an MCP client -----------------------
async def _mcp_check_inventory(sku: str) -> str:
    params = StdioServerParameters(
        command=sys.executable, args=["-m", "day3.retail_multi_agent.mcp_inventory_server"]
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("check_inventory", {"sku": sku})
            return result.content[0].text if result.content else "{}"


@tool
def inventory_check(sku: str) -> str:
    """[MCP] Check live inventory for a SKU (e.g. GV-MILK-1G) via the Inventory MCP server."""
    return asyncio.run(_mcp_check_inventory(sku))


# --- RAG integration: Policy agent retrieves from a FAISS knowledge base ------
_VECTOR_STORE: FAISS | None = None


def _policy_store() -> FAISS:
    global _VECTOR_STORE
    if _VECTOR_STORE is None:
        documents = [
            Document(page_content=path.read_text(encoding="utf-8"), metadata={"source": path.name})
            for path in sorted(DOCS_DIR.glob("*.md"))
            if path.name.lower() != "readme.md"
        ]
        chunks = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100).split_documents(
            documents
        )
        embeddings = OpenAIEmbeddings(
            api_key=settings.openai_api_key.get_secret_value(),
            model="text-embedding-3-small",
        )
        _VECTOR_STORE = FAISS.from_documents(chunks, embeddings)
    return _VECTOR_STORE


@tool
def policy_lookup(question: str) -> str:
    """[RAG] Retrieve relevant store-policy text from the policy knowledge base.

    Use for returns, refunds, shipping, pickup, and price-match questions.
    """
    documents = _policy_store().as_retriever(search_kwargs={"k": 3}).invoke(question)
    if not documents:
        return "No policy text found."
    return "\n\n".join(
        f"[source: {doc.metadata.get('source')}]\n{doc.page_content}" for doc in documents
    )


# --- Registry: one entry per specialist agent --------------------------------
DOMAINS: dict[str, dict] = {
    "product": {
        "integration": "REST",
        "tools": [product_search],
        "prompt": (
            "You are the Walmart PRODUCT agent. Use the Product Service tool to answer "
            "product, price, aisle, and SKU questions. Always report the SKU."
        ),
    },
    "inventory": {
        "integration": "MCP",
        "tools": [inventory_check],
        "prompt": (
            "You are the Walmart INVENTORY agent. Use the Inventory MCP tool to report "
            "live stock for a SKU. SKUs look like GV-MILK-1G. If you were given a product "
            "but not a SKU, use the SKU from the provided context."
        ),
    },
    "orders": {
        "integration": "REST",
        "tools": [order_status],
        "prompt": (
            "You are the Walmart ORDERS agent. Use the Orders Service tool to report order "
            "status by id (WM-2024-00X)."
        ),
    },
    "policy": {
        "integration": "RAG",
        "tools": [policy_lookup],
        "prompt": (
            "You are the Walmart POLICY agent. Answer ONLY from the retrieved policy text "
            "and cite the source file. If the policy text does not cover it, say so."
        ),
    },
}

DOMAIN_ORDER = ["product", "inventory", "orders", "policy"]
