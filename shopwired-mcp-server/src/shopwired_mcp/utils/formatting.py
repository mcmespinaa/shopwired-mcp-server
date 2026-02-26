"""Response formatting utilities.

Transforms raw ShopWired API JSON into clean, AI-readable text.
"""

from __future__ import annotations

from typing import Any


def format_price(pence: Any) -> str:
    """Format price from pence (integer) to pounds string.

    ShopWired stores prices in pence (e.g., 9000 = £90.00).
    """
    try:
        value = float(pence or 0)
        if value >= 100:
            return f"£{value / 100:.2f}"
        else:
            return f"£{value:.2f}"
    except (TypeError, ValueError):
        return "£0.00"


def format_product(product: dict[str, Any]) -> str:
    """Format a product dict into a readable summary."""
    # ShopWired uses 'title' not 'name'
    title = product.get("title", product.get("name", "Unknown"))
    # ShopWired uses 'active' (boolean/0-1) not 'status' (string)
    active = product.get("active")
    if active is True or active == 1:
        status = "Active"
    elif active is False or active == 0:
        status = "Hidden"
    else:
        status = product.get("status", "N/A")

    lines = [
        f"Product: {title}",
        f"  ID: {product.get('id', 'N/A')}",
        f"  SKU: {product.get('sku', 'N/A')}",
        f"  Price: {format_price(product.get('price'))}",
    ]
    if product.get("salePrice") or product.get("sale_price"):
        lines.append(f"  Sale Price: {format_price(product.get('salePrice', product.get('sale_price')))}")
    if product.get("comparePrice"):
        lines.append(f"  Compare Price: {format_price(product.get('comparePrice'))}")
    lines.extend([
        f"  Stock: {product.get('stock', product.get('stock_level', 'N/A'))}",
        f"  Status: {status}",
    ])
    if product.get("url"):
        lines.append(f"  URL: {product['url']}")
    cat = product.get("category", {})
    if isinstance(cat, dict) and cat.get("name"):
        lines.append(f"  Category: {cat['name']}")
    brand = product.get("brand", {})
    if isinstance(brand, dict) and brand.get("name"):
        lines.append(f"  Brand: {brand['name']}")
    if product.get("description"):
        desc = product["description"][:300]
        if len(product["description"]) > 300:
            desc += "..."
        lines.append(f"  Description: {desc}")
    return "\n".join(lines)


def format_product_list(products: list[dict[str, Any]], total: int | None = None) -> str:
    """Format a list of products."""
    if not products:
        return "No products found."
    header = f"Found {total or len(products)} product(s):\n"
    items = [format_product(p) for p in products]
    return header + "\n---\n".join(items)


def format_order(order: dict[str, Any]) -> str:
    """Format an order dict into a readable summary."""
    reference = order.get("reference", order.get("orderReference", ""))
    status = order.get("status", order.get("orderStatus", "N/A"))
    total = order.get("total", order.get("orderTotal", 0))
    created = order.get("createdAt", order.get("dateCreated", order.get("created_at", "N/A")))

    lines = [
        f"Order #{order.get('id', 'N/A')}" + (f" ({reference})" if reference else ""),
        f"  Status: {status}",
        f"  Date: {created}",
        f"  Total: {format_price(total)}" if total else "  Total: N/A",
        f"  Currency: {order.get('currency', 'N/A')}",
        f"  Payment Status: {order.get('payment_status', 'N/A')}",
    ]
    # Customer info — might be nested or flat
    customer = order.get("customer", {})
    if isinstance(customer, dict):
        name = f"{customer.get('firstName', customer.get('first_name', ''))} {customer.get('lastName', customer.get('last_name', ''))}".strip()
        if name:
            lines.append(f"  Customer: {name}")
        email = customer.get("email", "")
        if email:
            lines.append(f"  Email: {email}")
    else:
        customer_name = order.get("customerName", order.get("firstName", ""))
        if customer_name:
            lines.append(f"  Customer: {customer_name}")
        customer_email = order.get("customerEmail", order.get("email", ""))
        if customer_email:
            lines.append(f"  Email: {customer_email}")

    # Line items
    items = order.get("items", [])
    if items:
        lines.append(f"  Items ({len(items)}):")
        for item in items[:10]:
            qty = item.get("quantity", 1)
            item_name = item.get("name", item.get("title", "Unknown"))
            price = format_price(item.get("price"))
            lines.append(f"    - {qty}x {item_name} @ {price}")
        if len(items) > 10:
            lines.append(f"    ... and {len(items) - 10} more items")

    return "\n".join(lines)


def format_order_list(orders: list[dict[str, Any]], total: int | None = None) -> str:
    """Format a list of orders."""
    if not orders:
        return "No orders found."
    header = f"Found {total or len(orders)} order(s):\n"
    items = [format_order(o) for o in orders]
    return header + "\n---\n".join(items)


def format_customer(customer: dict[str, Any]) -> str:
    """Format a customer dict into a readable summary."""
    first = customer.get("firstName", customer.get("first_name", ""))
    last = customer.get("lastName", customer.get("last_name", ""))
    name = f"{first} {last}".strip()
    lines = [
        f"Customer: {name or 'Unknown'}",
        f"  ID: {customer.get('id', 'N/A')}",
        f"  Email: {customer.get('email', 'N/A')}",
    ]
    phone = customer.get("phone", customer.get("telephone", ""))
    if phone:
        lines.append(f"  Phone: {phone}")
    company = customer.get("company", "")
    if company:
        lines.append(f"  Company: {company}")
    created = customer.get("createdAt", customer.get("created_at", ""))
    if created:
        lines.append(f"  Created: {created}")
    return "\n".join(lines)


def format_customer_list(customers: list[dict[str, Any]], total: int | None = None) -> str:
    """Format a list of customers."""
    if not customers:
        return "No customers found."
    header = f"Found {total or len(customers)} customer(s):\n"
    items = [format_customer(c) for c in customers]
    return header + "\n---\n".join(items)


def format_category(category: dict[str, Any]) -> str:
    """Format a category."""
    name = category.get("name", category.get("title", "Unknown"))
    desc = category.get("description", "")
    line = f"Category: {name} (ID: {category.get('id', 'N/A')})"
    if desc:
        desc_preview = desc[:100].strip()
        if len(desc) > 100:
            desc_preview += "..."
        line += f" — {desc_preview}"
    return line


def format_voucher(voucher: dict[str, Any]) -> str:
    """Format a voucher/discount code."""
    voucher_type = voucher.get("type", voucher.get("voucherType", "N/A"))
    value = voucher.get("value", voucher.get("amount", "N/A"))
    active = voucher.get("active", None)
    status = "Active" if active else "Inactive" if active is not None else "N/A"
    lines = [
        f"Voucher: {voucher.get('code', 'N/A')}",
        f"  ID: {voucher.get('id', 'N/A')}",
        f"  Type: {voucher_type}",
        f"  Value: {value}",
        f"  Status: {status}",
    ]
    return "\n".join(lines)


def format_generic_list(
    items: list[dict[str, Any]], resource_name: str, key_field: str = "name"
) -> str:
    """Generic formatter for simple resource lists."""
    if not items:
        return f"No {resource_name} found."
    lines = [f"Found {len(items)} {resource_name}:"]
    for item in items:
        name = item.get(key_field, item.get("title", item.get("code", f"item {item.get('id', 'N/A')}")))
        lines.append(f"  - {name} (ID: {item.get('id', 'N/A')})")
    return "\n".join(lines)
