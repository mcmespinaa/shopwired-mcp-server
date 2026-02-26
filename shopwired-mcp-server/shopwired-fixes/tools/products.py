"""Product management tools for ShopWired MCP server."""

from shopwired_mcp.client import api_client
from shopwired_mcp.utils.formatting import format_product, format_product_list, format_generic_list


async def search_products(query: str, count: int = 20) -> str:
    """Search for products by keyword.

    Args:
        query: Search term to match against product names and descriptions
        count: Maximum number of results to return (default: 20, max: 250)
    """
    # ShopWired search endpoint: GET /products/search?query=...
    params = {"query": query}
    if count:
        params["count"] = min(count, 250)

    data = await api_client.get("products/search", params=params)

    if isinstance(data, list):
        return format_product_list(data)
    elif isinstance(data, dict) and "products" in data:
        return format_product_list(data["products"], total=data.get("total"))
    elif isinstance(data, dict):
        # Might be a single result or wrapped differently
        return format_product_list([data] if data.get("id") else [])
    return "No products found."


async def get_product(product_id: int) -> str:
    """Get full details for a specific product by its ID.

    Args:
        product_id: The numeric ID of the product
    """
    # Request embedded data for full details
    data = await api_client.get(
        f"products/{product_id}",
        params={"embed": "images,brand,categories,variations,extras,options"}
    )
    return format_product(data)


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
    params: dict = {"count": min(count, 250)}
    if offset:
        params["offset"] = offset
    if active is not None:
        params["active"] = 1 if active else 0
    if sort:
        params["sort"] = sort
    if embed:
        params["embed"] = embed

    data = await api_client.get("products", params=params)

    if isinstance(data, list):
        return format_product_list(data)
    elif isinstance(data, dict) and "products" in data:
        return format_product_list(data["products"], total=data.get("total"))
    return "No products found."


async def create_product(
    title: str,
    price: float = 0,
    description: str = "",
    sku: str = "",
    stock: int | None = None,
    active: bool = True,
    weight: float | None = None,
) -> str:
    """Create a new product in the store.

    Args:
        title: Product title (required)
        price: Product price in pence (e.g., 9999 = £99.99)
        description: Product description (HTML allowed)
        sku: Stock Keeping Unit code
        stock: Initial stock quantity
        active: Whether the product is active (default: True)
        weight: Product weight
    """
    payload: dict = {"title": title}
    if price:
        payload["price"] = price
    if description:
        payload["description"] = description
    if sku:
        payload["sku"] = sku
    if stock is not None:
        payload["stock"] = stock
    if weight is not None:
        payload["weight"] = weight
    payload["active"] = active

    data = await api_client.post("products", json_data=payload)
    return f"Product created successfully:\n{format_product(data)}"


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
    payload: dict = {}
    if title is not None:
        payload["title"] = title
    if price is not None:
        payload["price"] = price
    if description is not None:
        payload["description"] = description
    if sku is not None:
        payload["sku"] = sku
    if active is not None:
        payload["active"] = active
    if weight is not None:
        payload["weight"] = weight

    if not payload:
        return "No fields to update. Provide at least one field to change."

    data = await api_client.put(f"products/{product_id}", json_data=payload)
    return f"Product updated successfully:\n{format_product(data)}"


async def delete_product(product_id: int) -> str:
    """Delete a product from the store. This action cannot be undone.

    Args:
        product_id: The numeric ID of the product to delete
    """
    await api_client.delete(f"products/{product_id}")
    return f"Product {product_id} deleted successfully."


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
        endpoint = f"products/{product_id}/variations/{variation_id}"
        data = await api_client.put(endpoint, json_data={"stock": stock})
        return f"Stock updated for variation {variation_id}: {stock} units"
    else:
        data = await api_client.put(f"products/{product_id}", json_data={"stock": stock})
        return f"Stock updated for product {product_id}: {stock} units"


async def list_product_variations(product_id: int) -> str:
    """List all variations (size, color, etc.) for a product.

    Args:
        product_id: The product ID
    """
    data = await api_client.get(f"products/{product_id}/variations")
    if isinstance(data, list):
        if not data:
            return f"No variations found for product {product_id}."
        lines = [f"Variations for product {product_id}:\n"]
        for v in data:
            vid = v.get("id", "N/A")
            price = v.get("price", 0)
            sku = v.get("sku", "")
            stock = v.get("stock", "N/A")
            values = v.get("values", [])
            opts = ", ".join(
                f"{val.get('optionName', 'Option')}: {val.get('name', val.get('value', ''))}"
                for val in values
            ) if values else "No options"
            lines.append(f"  • ID {vid}: {opts} | Price: {price} | SKU: {sku} | Stock: {stock}")
        return "\n".join(lines)
    return format_generic_list(data if isinstance(data, list) else [], "variation")


async def list_product_images(product_id: int) -> str:
    """List all images for a product.

    Args:
        product_id: The product ID
    """
    data = await api_client.get(f"products/{product_id}/images")
    if isinstance(data, list):
        if not data:
            return f"No images found for product {product_id}."
        lines = [f"Images for product {product_id}:\n"]
        for img in data:
            img_id = img.get("id", "N/A")
            url = img.get("url", img.get("src", "N/A"))
            position = img.get("position", img.get("sortOrder", ""))
            lines.append(f"  • ID {img_id}: {url}" + (f" (position: {position})" if position else ""))
        return "\n".join(lines)
    return f"No images found for product {product_id}."


async def get_product_count(active: bool | None = None) -> str:
    """Get the total number of products in the store.

    Args:
        active: Filter by active status (True=active, False=hidden, None=all)
    """
    params = {}
    if active is not None:
        params["active"] = 1 if active else 0

    data = await api_client.get("products/count", params=params)

    if isinstance(data, dict):
        count = data.get("count", data.get("total", "unknown"))
        return f"Total products: {count}"
    return f"Total products: {data}"
