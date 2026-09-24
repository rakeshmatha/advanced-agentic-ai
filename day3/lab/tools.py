from __future__ import annotations

from langchain_core.tools import tool


@tool
def search_product(query: str) -> str:
    """Search the product catalog. Returns product name, price, aisle, and SKU."""
    catalog = {
        "milk": "Great Value Whole Milk 1gal | $3.98 | Aisle 12 | SKU: GV-MILK-1G",
        "bread": "Great Value White Bread 20oz | $1.28 | Aisle 8 | SKU: GV-BREAD-20",
        "eggs": "Great Value Large Eggs 12ct | $2.68 | Aisle 11 | SKU: GV-EGGS-12",
        "butter": "Great Value Unsalted Butter 1lb | $4.48 | Aisle 12 | SKU: GV-BUTT-1",
        "chicken": "Great Value Chicken Breast 3lb | $8.97 | Aisle 4 | SKU: GV-CHKN-3",
    }
    lowered = query.lower()
    for key, value in catalog.items():
        if key in lowered:
            return value
    return (
        f"No product found for: {query}. Available: milk, bread, eggs, butter, chicken"
    )


@tool
def check_inventory(sku: str) -> str:
    """Check inventory for a product SKU at the nearest store."""
    inventory = {
        "GV-MILK-1G": "In stock: 24 units | Store 042 Bentonville AR",
        "GV-BREAD-20": "In stock: 61 units | Store 042 Bentonville AR",
        "GV-EGGS-12": "Low stock: 5 units | Store 042 | Restock: Tomorrow",
        "GV-BUTT-1": "In stock: 18 units | Store 042 Bentonville AR",
        "GV-CHKN-3": "Out of stock | Store 042 | Available for online order",
    }
    return inventory.get(sku.upper(), f"SKU {sku} not found in inventory system")


@tool
def get_policy(policy_type: str) -> str:
    """Retrieve store policy. Types: returns, shipping, price_match, pickup, grocery."""
    policies = {
        "returns": "90-day return policy. Receipt required. Electronics: 15 days.",
        "shipping": "Free 2-day shipping on orders over $35. Same-day delivery in select areas.",
        "price_match": "Walmart matches Amazon, Target, and major retailers on identical items.",
        "pickup": "Free curbside pickup. Order by 6pm for same-day at most stores.",
        "grocery": "Fresh guarantee: full refund on any fresh item if not satisfied.",
    }
    key = policy_type.lower().replace(" ", "_")
    for name, value in policies.items():
        if name in key or key in name:
            return value
    return (
        f"Policy not found: {policy_type}. Available: returns, shipping, "
        "price_match, pickup, grocery"
    )


@tool
def get_order_status(order_id: str) -> str:
    """Get current status of an order by order ID."""
    orders = {
        "WM-2024-001": "Delivered June 28 2026 | 3 items | Total: $24.73",
        "WM-2024-002": "Out for delivery | ETA: Today by 8pm",
        "WM-2024-003": "Processing | Payment confirmed | Ships within 24 hours",
        "WM-2024-004": "Cancelled | Refund of $18.45 issued June 27 2026",
    }
    return orders.get(
        order_id.upper(),
        f"Order {order_id} not found. Valid: WM-2024-001 to WM-2024-004",
    )


ALL_TOOLS = [search_product, check_inventory, get_policy, get_order_status]
PRODUCT_TOOLS = [search_product, check_inventory]
SERVICE_TOOLS = [get_policy, get_order_status]
ORDER_TOOLS = [get_order_status, get_policy]

TEST_QUERIES = [
    "What is the price of milk and is it in stock?",
    "I want to return a TV I bought 10 days ago. What is the return policy?",
    "Check my order WM-2024-002.",
    "Find chicken breast and tell me if I can pick it up today.",
    "Do you price match? I saw eggs cheaper at Target.",
]

EXPECTED_ROUTES = {
    TEST_QUERIES[0]: "product",
    TEST_QUERIES[1]: "service",
    TEST_QUERIES[2]: "order",
    TEST_QUERIES[3]: "product",
    TEST_QUERIES[4]: "service",
}
