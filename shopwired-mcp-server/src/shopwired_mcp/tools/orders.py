"""Order management MCP tools.

Exposes tools for listing, viewing, searching, updating, and managing
orders in a ShopWired store.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..client import api_client
from ..utils.formatting import format_order, format_order_list


def register_order_tools(mcp: FastMCP) -> None:
    """Register all order-related tools with the MCP server."""

    @mcp.tool()
    async def list_orders(
        count: int = 50,
        offset: int = 0,
        status: str | None = None,
    ) -> str:
        """List orders from the store with optional filters.

        Args:
            count: Number of orders per page (default: 50, max: 250)
            offset: Number of orders to skip for pagination (default: 0)
            status: Filter by order status (e.g., 'pending', 'processing', 'shipped', 'completed')
        """
        params: dict[str, Any] = {"count": min(count, 250)}
        if offset:
            params["offset"] = offset
        if status:
            params["status"] = status

        data = await api_client.get("/orders", params=params)

        if isinstance(data, list):
            return format_order_list(data)
        elif isinstance(data, dict) and "orders" in data:
            return format_order_list(data["orders"], total=data.get("total"))
        return "No orders found."

    @mcp.tool()
    async def get_order(order_id: int) -> str:
        """Get full details for a specific order.

        Args:
            order_id: The numeric order ID
        """
        data = await api_client.get(f"/orders/{order_id}")
        order = data.get("data", data) if isinstance(data, dict) else data
        return format_order(order)

    @mcp.tool()
    async def search_orders(
        query: str,
        count: int = 20,
    ) -> str:
        """Search orders by keyword (matches order ID, customer name, email, etc.).

        Args:
            query: Search term
            count: Maximum results (default: 20)
        """
        params: dict[str, Any] = {"query": query}
        if count:
            params["count"] = min(count, 250)

        data = await api_client.get("/orders/search", params=params)

        if isinstance(data, list):
            return format_order_list(data)
        elif isinstance(data, dict) and "orders" in data:
            return format_order_list(data["orders"], total=data.get("total"))
        return "No orders found."

    @mcp.tool()
    async def get_order_count(status: str | None = None) -> str:
        """Get the total number of orders, optionally filtered.

        Args:
            status: Filter by status
        """
        params: dict[str, Any] = {}
        if status:
            params["status"] = status

        data = await api_client.get("/orders/count", params=params)

        if isinstance(data, dict):
            count = data.get("count", data.get("total", "unknown"))
            return f"Total orders: {count}"
        return f"Total orders: {data}"

    @mcp.tool()
    async def update_order_status(
        order_id: int,
        status: str,
        notify_customer: bool = False,
    ) -> str:
        """Update the status of an order.

        Args:
            order_id: The order ID to update
            status: New status (e.g., 'processing', 'shipped', 'completed', 'cancelled')
            notify_customer: Whether to send a notification email to the customer (default: False)
        """
        body: dict[str, Any] = {"status": status}
        if notify_customer:
            body["notifyCustomer"] = True

        # ShopWired uses POST /orders/{id}/status
        await api_client.post(f"/orders/{order_id}/status", body)
        return f"Order {order_id} status updated to '{status}'."

    @mcp.tool()
    async def add_order_comment(
        order_id: int,
        comment: str,
    ) -> str:
        """Add an admin comment to an order (internal note, not visible to customer).

        Args:
            order_id: The order ID
            comment: The comment text to add
        """
        # ShopWired uses POST /orders/{id}/comments
        await api_client.post(f"/orders/{order_id}/comments", {"comment": comment})
        return f"Comment added to order {order_id}."

    @mcp.tool()
    async def delete_order(order_id: int) -> str:
        """Delete an order. This action cannot be undone.

        Args:
            order_id: The numeric order ID to delete
        """
        await api_client.delete(f"/orders/{order_id}")
        return f"Order #{order_id} deleted successfully."
