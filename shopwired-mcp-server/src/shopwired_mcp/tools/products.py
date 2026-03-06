"""Product management MCP tools.

Exposes tools for searching, viewing, creating, updating, and deleting
products in a ShopWired store, plus stock and image management.
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from ..client import api_client

logger = logging.getLogger(__name__)
from ..utils.formatting import format_product, format_product_list, format_generic_list


def register_product_tools(mcp: FastMCP) -> None:
    """Register all product-related tools with the MCP server."""

    @mcp.tool()
    async def search_products(
        query: str,
        count: int = 20,
    ) -> str:
        """Search ShopWired products by keyword.

        Args:
            query: Search term to match against product names and descriptions
            count: Maximum number of results to return (default: 20, max: 250)
        """
        if not query.strip():
            return "Search query cannot be empty."
        if count < 1:
            return "Count must be at least 1."
        params: dict[str, Any] = {"query": query}
        params["count"] = min(count, 250)

        data = await api_client.get("/products/search", params=params)

        if isinstance(data, list):
            return format_product_list(data)
        elif isinstance(data, dict) and "products" in data:
            return format_product_list(data["products"], total=data.get("total"))
        elif isinstance(data, dict):
            return format_product_list([data] if data.get("id") else [])
        return "No products found."

    @mcp.tool()
    async def get_product(product_id: int) -> str:
        """Get full details for a specific product by its ID.

        Args:
            product_id: The numeric ID of the product
        """
        # Request embedded data for full details
        if product_id < 1:
            return "Invalid product ID."
        data = await api_client.get(
            f"/products/{product_id}",
            params={"embed": "images,brand,categories,variations,extras,options"},
        )
        product = data.get("data", data) if isinstance(data, dict) else data
        return format_product(product)

    @mcp.tool()
    async def list_products(
        count: int = 50,
        offset: int = 0,
        active: bool | None = None,
        sort: str | None = None,
        embed: str | None = None,
    ) -> str:
        """List products from the store with optional filters.

        Args:
            count: Number of products per page (default: 50, max: 250)
            offset: Number of products to skip for pagination (default: 0)
            active: Filter by active status (True=active, False=hidden)
            sort: Sort order - 'title', 'title_desc', or leave empty for creation date
            embed: Comma-separated related data to include (e.g. 'images,brand,categories')
        """
        if count < 1:
            return "Count must be at least 1."
        if offset < 0:
            return "Offset cannot be negative."
        params: dict[str, Any] = {"count": min(count, 250)}
        if offset:
            params["offset"] = offset
        if active is not None:
            params["active"] = 1 if active else 0
        if sort:
            params["sort"] = sort
        if embed:
            params["embed"] = embed

        data = await api_client.get("/products", params=params)

        if isinstance(data, list):
            return format_product_list(data)
        elif isinstance(data, dict) and "products" in data:
            return format_product_list(data["products"], total=data.get("total"))
        return "No products found."

    @mcp.tool()
    async def create_product(
        title: str,
        price: float = 0,
        description: str = "",
        sku: str = "",
        stock: int | None = None,
        active: bool = True,
        weight: float | None = None,
    ) -> str:
        """Create a new product in the ShopWired store.

        Args:
            title: Product title (required)
            price: Product price in pence (e.g., 9999 = £99.99)
            description: Product description (HTML allowed)
            sku: Stock Keeping Unit code
            stock: Initial stock quantity
            active: Whether the product is active (default: True)
            weight: Product weight
        """
        if not title.strip():
            return "Product title cannot be empty."
        logger.info("create_product called: title=%r", title)
        body: dict[str, Any] = {"title": title}
        if price:
            body["price"] = price
        if description:
            body["description"] = description
        if sku:
            body["sku"] = sku
        if stock is not None:
            body["stock"] = stock
        if weight is not None:
            body["weight"] = weight
        body["active"] = active

        data = await api_client.post("/products", body)
        product = data.get("data", data) if isinstance(data, dict) else data
        return f"Product created successfully!\n\n{format_product(product)}"

    @mcp.tool()
    async def update_product(
        product_id: int,
        title: str | None = None,
        price: float | None = None,
        description: str | None = None,
        sku: str | None = None,
        active: bool | None = None,
        weight: float | None = None,
    ) -> str:
        """Update an existing product. Only provided fields will be changed.

        Args:
            product_id: The numeric ID of the product to update (required)
            title: New product title
            price: New price in pence
            description: New description (HTML allowed)
            sku: New SKU code
            active: Set active (True) or hidden (False)
            weight: New weight
        """
        if product_id < 1:
            return "Invalid product ID."
        if title is not None and not title.strip():
            return "Product title cannot be empty."
        body: dict[str, Any] = {}
        if title is not None:
            body["title"] = title
        if price is not None:
            body["price"] = price
        if description is not None:
            body["description"] = description
        if sku is not None:
            body["sku"] = sku
        if active is not None:
            body["active"] = active
        if weight is not None:
            body["weight"] = weight

        if not body:
            return "No fields provided to update."

        data = await api_client.put(f"/products/{product_id}", body)
        product = data.get("data", data) if isinstance(data, dict) else data
        return f"Product updated successfully!\n\n{format_product(product)}"

    @mcp.tool()
    async def delete_product(product_id: int, confirm: bool = False) -> str:
        """Delete a product from the store. This action cannot be undone.

        Args:
            product_id: The numeric ID of the product to delete
            confirm: Must be True to execute the deletion. Defaults to False as a safety measure.
        """
        if product_id < 1:
            return "Invalid product ID."
        if not confirm:
            return f"This will permanently delete product {product_id}. Call again with confirm=True to proceed."
        logger.info("delete_product confirmed: product_id=%d", product_id)
        await api_client.delete(f"/products/{product_id}")
        return f"Product {product_id} deleted successfully."

    @mcp.tool()
    async def update_stock(
        product_id: int,
        stock: int,
        variation_id: int | None = None,
    ) -> str:
        """Update stock level for a product or a specific variation.

        Args:
            product_id: The product ID
            stock: New stock quantity
            variation_id: Optional variation ID (for products with size/color variants)
        """
        if variation_id:
            path = f"/products/{product_id}/variations/{variation_id}"
            data = await api_client.put(path, {"stock": stock})
            return f"Stock updated for variation {variation_id}: {stock} units"
        else:
            data = await api_client.put(f"/products/{product_id}", {"stock": stock})
            return f"Stock updated for product {product_id}: {stock} units"

    @mcp.tool()
    async def list_product_variations(product_id: int) -> str:
        """List all variations (size, color, etc.) for a product.

        Args:
            product_id: The product ID
        """
        data = await api_client.get(f"/products/{product_id}/variations")
        variations = data if isinstance(data, list) else data.get("data", [])

        if not variations:
            return f"Product {product_id} has no variations."

        lines = [f"Variations for product {product_id}:\n"]
        for v in variations:
            vid = v.get("id", "N/A")
            price = v.get("price", 0)
            sku = v.get("sku", "")
            stock = v.get("stock", v.get("stock_level", "N/A"))
            values = v.get("values", [])
            opts = ", ".join(
                f"{val.get('optionName', 'Option')}: {val.get('name', val.get('value', ''))}"
                for val in values
            ) if values else v.get("name", "No options")
            lines.append(f"  - ID {vid}: {opts} | Price: {price} | SKU: {sku} | Stock: {stock}")
        return "\n".join(lines)

    @mcp.tool()
    async def list_product_images(product_id: int) -> str:
        """List all images for a product.

        Args:
            product_id: The product ID
        """
        data = await api_client.get(f"/products/{product_id}/images")
        images = data if isinstance(data, list) else data.get("data", [])

        if not images:
            return f"Product {product_id} has no images."

        lines = [f"Images for product {product_id}:\n"]
        for img in images:
            img_id = img.get("id", "N/A")
            url = img.get("url", img.get("src", "N/A"))
            position = img.get("position", img.get("sortOrder", ""))
            lines.append(f"  - ID {img_id}: {url}" + (f" (position: {position})" if position else ""))
        return "\n".join(lines)

    @mcp.tool()
    async def get_product_count(active: bool | None = None) -> str:
        """Get the total number of products in the store.

        Args:
            active: Filter by active status (True=active, False=hidden, None=all)
        """
        params: dict[str, Any] = {}
        if active is not None:
            params["active"] = 1 if active else 0

        data = await api_client.get("/products/count", params=params)

        if isinstance(data, dict):
            count = data.get("count", data.get("total", "unknown"))
            return f"Total products: {count}"
        return f"Total products: {data}"
