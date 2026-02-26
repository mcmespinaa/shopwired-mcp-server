"""Store configuration MCP tools.

Covers categories, brands, tags, vouchers, gift cards, shipping,
webhooks, and business details.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..client import api_client
from ..utils.formatting import format_category, format_generic_list, format_voucher


def register_store_tools(mcp: FastMCP) -> None:
    """Register all store-configuration tools with the MCP server."""

    # ── Categories ────────────────────────────────────────────────────

    @mcp.tool()
    async def list_categories(count: int = 100, offset: int = 0) -> str:
        """List all product categories.

        Args:
            count: Results per page (default: 100)
            offset: Number to skip for pagination
        """
        params: dict[str, Any] = {"count": min(count, 250)}
        if offset:
            params["offset"] = offset

        data = await api_client.get("/categories", params=params)
        categories = data if isinstance(data, list) else data.get("categories", data.get("data", []))
        if not categories:
            return "No categories found."
        return "\n\n".join(format_category(c) for c in categories)

    @mcp.tool()
    async def create_category(
        name: str,
        description: str = "",
        parent_id: int | None = None,
    ) -> str:
        """Create a new product category.

        Args:
            name: Category name (required)
            description: Category description
            parent_id: Parent category ID for nested categories
        """
        body: dict[str, Any] = {"name": name}
        if description:
            body["description"] = description
        if parent_id is not None:
            body["parentId"] = parent_id
        data = await api_client.post("/categories", body)
        cat = data.get("data", data) if isinstance(data, dict) else data
        return f"Category created!\n{format_category(cat)}"

    @mcp.tool()
    async def update_category(
        category_id: int,
        name: str | None = None,
        description: str | None = None,
    ) -> str:
        """Update an existing category.

        Args:
            category_id: The category ID to update
            name: New name
            description: New description
        """
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if not body:
            return "No fields provided to update."
        data = await api_client.put(f"/categories/{category_id}", body)
        cat = data.get("data", data) if isinstance(data, dict) else data
        return f"Category updated!\n{format_category(cat)}"

    @mcp.tool()
    async def delete_category(category_id: int) -> str:
        """Delete a category. Products in this category will become uncategorized.

        Args:
            category_id: The category ID to delete
        """
        await api_client.delete(f"/categories/{category_id}")
        return f"Category {category_id} deleted."

    # ── Brands ────────────────────────────────────────────────────────

    @mcp.tool()
    async def list_brands(count: int = 100, offset: int = 0) -> str:
        """List all product brands.

        Args:
            count: Results per page
            offset: Number to skip for pagination
        """
        params: dict[str, Any] = {"count": min(count, 250)}
        if offset:
            params["offset"] = offset

        data = await api_client.get("/brands", params=params)
        items = data if isinstance(data, list) else data.get("brands", data.get("data", []))
        return format_generic_list(items, "brand")

    @mcp.tool()
    async def create_brand(name: str, description: str = "") -> str:
        """Create a new brand.

        Args:
            name: Brand name (required)
            description: Brand description
        """
        body: dict[str, Any] = {"name": name}
        if description:
            body["description"] = description
        data = await api_client.post("/brands", body)
        brand = data.get("data", data) if isinstance(data, dict) else data
        return f"Brand created: {brand.get('name', name)} (ID: {brand.get('id', 'N/A')})"

    # ── Vouchers ──────────────────────────────────────────────────────

    @mcp.tool()
    async def list_vouchers(count: int = 50, offset: int = 0) -> str:
        """List all voucher/discount codes.

        Args:
            count: Results per page
            offset: Number to skip for pagination
        """
        params: dict[str, Any] = {"count": min(count, 250)}
        if offset:
            params["offset"] = offset

        data = await api_client.get("/vouchers", params=params)
        items = data if isinstance(data, list) else data.get("vouchers", data.get("data", []))
        if not items:
            return "No vouchers found."
        return "\n\n".join(format_voucher(v) for v in items)

    @mcp.tool()
    async def create_voucher(
        code: str,
        voucher_type: str,
        value: float,
        active: bool = True,
        min_order_value: float | None = None,
        usage_limit: int | None = None,
        expiry_date: str | None = None,
    ) -> str:
        """Create a new voucher/discount code.

        Args:
            code: The discount code customers will enter (required)
            voucher_type: Type of discount — 'percentage', 'fixed', or 'free_shipping'
            value: Discount value (percentage or fixed amount)
            active: Whether the voucher is active (default: True)
            min_order_value: Minimum order value to use the voucher
            usage_limit: Maximum number of times this voucher can be used
            expiry_date: Expiry date in YYYY-MM-DD format
        """
        body: dict[str, Any] = {
            "code": code,
            "type": voucher_type,
            "value": value,
            "active": active,
        }
        if min_order_value is not None:
            body["minOrderValue"] = min_order_value
        if usage_limit is not None:
            body["usageLimit"] = usage_limit
        if expiry_date:
            body["expiryDate"] = expiry_date

        data = await api_client.post("/vouchers", body)
        voucher = data.get("data", data) if isinstance(data, dict) else data
        return f"Voucher created!\n{format_voucher(voucher)}"

    @mcp.tool()
    async def delete_voucher(voucher_id: int) -> str:
        """Delete a voucher.

        Args:
            voucher_id: The voucher ID to delete
        """
        await api_client.delete(f"/vouchers/{voucher_id}")
        return f"Voucher {voucher_id} deleted."

    # ── Gift Cards ────────────────────────────────────────────────────

    @mcp.tool()
    async def list_gift_cards(count: int = 50, offset: int = 0) -> str:
        """List all gift cards.

        Args:
            count: Results per page
            offset: Number to skip for pagination
        """
        params: dict[str, Any] = {"count": min(count, 250)}
        if offset:
            params["offset"] = offset

        data = await api_client.get("/gift-cards", params=params)
        items = data if isinstance(data, list) else data.get("giftCards", data.get("data", []))
        return format_generic_list(items, "gift card")

    # ── Shipping ──────────────────────────────────────────────────────

    @mcp.tool()
    async def list_shipping_zones() -> str:
        """List all shipping zones configured in the store."""
        data = await api_client.get("/shipping-zones")
        items = data if isinstance(data, list) else data.get("shippingZones", data.get("data", []))
        return format_generic_list(items, "shipping zone")

    @mcp.tool()
    async def list_shipping_rates(zone_id: int) -> str:
        """List shipping rates for a specific zone.

        Args:
            zone_id: The shipping zone ID
        """
        data = await api_client.get(f"/shipping-zones/{zone_id}/rates")
        items = data if isinstance(data, list) else data.get("rates", data.get("data", []))
        if not items:
            return f"No shipping rates found for zone {zone_id}."
        lines = [f"Shipping rates for zone {zone_id}:\n"]
        for rate in items:
            rate_id = rate.get("id", "N/A")
            name = rate.get("name", rate.get("title", "Unnamed"))
            price = rate.get("price", rate.get("cost", "N/A"))
            lines.append(f"  - {name} (ID: {rate_id}) — £{price}")
        return "\n".join(lines)

    # ── Webhooks ──────────────────────────────────────────────────────

    @mcp.tool()
    async def list_webhooks() -> str:
        """List all configured webhooks."""
        data = await api_client.get("/webhooks")
        items = data if isinstance(data, list) else data.get("webhooks", data.get("data", []))
        if not items:
            return "No webhooks configured."
        lines = ["Configured webhooks:\n"]
        for wh in items:
            wh_id = wh.get("id", "N/A")
            event = wh.get("event", wh.get("topic", "N/A"))
            url = wh.get("url", wh.get("address", "N/A"))
            lines.append(f"  - ID {wh_id}: {event} → {url}")
        return "\n".join(lines)

    @mcp.tool()
    async def create_webhook(event: str, url: str) -> str:
        """Create a new webhook subscription.

        Args:
            event: The event to subscribe to (e.g., 'order.created', 'product.updated')
            url: The URL to receive webhook POST requests
        """
        data = await api_client.post("/webhooks", {"event": event, "url": url})
        hook = data.get("data", data) if isinstance(data, dict) else data
        return f"Webhook created: {hook.get('event', event)} → {hook.get('url', url)} (ID: {hook.get('id', 'N/A')})"

    # ── Business Details ──────────────────────────────────────────────

    @mcp.tool()
    async def get_business_details() -> str:
        """Get the store's business details (name, address, contact info)."""
        data = await api_client.get("/business-details")
        if isinstance(data, dict):
            lines = ["Business Details:\n"]
            for key, value in data.items():
                if value:
                    readable_key = "".join(
                        f" {c}" if c.isupper() else c for c in key
                    ).strip().title()
                    lines.append(f"  {readable_key}: {value}")
            return "\n".join(lines)
        return str(data)

    # ── Countries ─────────────────────────────────────────────────────

    @mcp.tool()
    async def list_countries() -> str:
        """List all available countries (for shipping configuration)."""
        data = await api_client.get("/countries")
        items = data if isinstance(data, list) else data.get("countries", data.get("data", []))
        return format_generic_list(items, "country")

    # ── Payment Methods ───────────────────────────────────────────────

    @mcp.tool()
    async def list_payment_methods() -> str:
        """List all payment methods configured in the store."""
        data = await api_client.get("/payment-methods")
        items = data if isinstance(data, list) else data.get("paymentMethods", data.get("data", []))
        if not items:
            return "No payment methods configured."
        lines = ["Payment methods:\n"]
        for pm in items:
            pm_id = pm.get("id", "N/A")
            name = pm.get("name", pm.get("title", "Unknown"))
            active = pm.get("active", None)
            status = " (Active)" if active else " (Inactive)" if active is not None else ""
            lines.append(f"  - {name}{status} (ID: {pm_id})")
        return "\n".join(lines)
