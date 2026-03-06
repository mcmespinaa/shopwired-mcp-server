"""Order management MCP tools.

Exposes tools for listing, viewing, searching, updating, and managing
orders in a ShopWired store.
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from ..client import api_client
from ..utils.formatting import format_order, format_order_list

logger = logging.getLogger(__name__)


def register_order_tools(mcp: FastMCP) -> None:
    """Register all order-related tools with the MCP server."""

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
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
        if count < 1:
            return "Count must be at least 1."
        if offset < 0:
            return "Offset cannot be negative."
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

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def get_order(order_id: int) -> str:
        """Get full details for a specific order.

        Args:
            order_id: The numeric order ID
        """
        if order_id < 1:
            return "Invalid order ID."
        data = await api_client.get(f"/orders/{order_id}")
        order = data.get("data", data) if isinstance(data, dict) else data
        return format_order(order)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def search_orders(
        query: str,
        count: int = 20,
    ) -> str:
        """Search orders by keyword (matches order ID, customer name, email, etc.).

        Args:
            query: Search term
            count: Maximum results (default: 20)
        """
        if not query.strip():
            return "Search query cannot be empty."
        if count < 1:
            return "Count must be at least 1."
        params: dict[str, Any] = {"query": query}
        params["count"] = min(count, 250)

        data = await api_client.get("/orders/search", params=params)

        if isinstance(data, list):
            return format_order_list(data)
        elif isinstance(data, dict) and "orders" in data:
            return format_order_list(data["orders"], total=data.get("total"))
        return "No orders found."

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
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

    @mcp.tool(annotations=ToolAnnotations(idempotentHint=True))
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
        if order_id < 1:
            return "Invalid order ID."
        if not status.strip():
            return "Status cannot be empty."
        body: dict[str, Any] = {"status": status}
        if notify_customer:
            body["notifyCustomer"] = True

        logger.info("update_order_status: order_id=%d, status=%r", order_id, status)
        # ShopWired uses POST /orders/{id}/status
        await api_client.post(f"/orders/{order_id}/status", body)
        return f"Order {order_id} status updated to '{status}'."

    @mcp.tool(annotations=ToolAnnotations(idempotentHint=False))
    async def add_order_comment(
        order_id: int,
        comment: str,
    ) -> str:
        """Add an admin comment to an order (internal note, not visible to customer).

        Args:
            order_id: The order ID
            comment: The comment text to add
        """
        if order_id < 1:
            return "Invalid order ID."
        if not comment.strip():
            return "Comment cannot be empty."
        # ShopWired uses POST /orders/{id}/comments
        await api_client.post(f"/orders/{order_id}/comments", {"comment": comment})
        return f"Comment added to order {order_id}."

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True))
    async def delete_order(order_id: int, confirm: bool = False) -> str:
        """Delete an order. This action cannot be undone.

        Args:
            order_id: The numeric order ID to delete
            confirm: Must be True to execute the deletion. Defaults to False as a safety measure.
        """
        if order_id < 1:
            return "Invalid order ID."
        if not confirm:
            return f"This will permanently delete order #{order_id}. Call again with confirm=True to proceed."
        logger.info("delete_order confirmed: order_id=%d", order_id)
        await api_client.delete(f"/orders/{order_id}")
        return f"Order #{order_id} deleted successfully."
