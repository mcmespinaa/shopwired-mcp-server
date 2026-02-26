"""Formatting utilities for ShopWired API responses."""

from typing import Any


def format_price(pence: Any) -> str:
    """Format price from pence (integer) to pounds string."""
    try:
        value = float(pence or 0)
        # ShopWired stores prices in pence (e.g., 9000 = £90.00)
        if value >= 100:
            return f"£{value / 100:.2f}"
        else:
            # If already in pounds (small values), display as-is
            return f"£{value:.2f}"
    except (TypeError, ValueError):
        return "£0.00"


def format_product(product: dict[str, Any]) -> str:
    """Format a single product for display."""
    product_id = product.get("id", "N/A")
    # ShopWired uses 'title' not 'name'
    title = product.get("title", "Untitled")
    sku = product.get("sku", "")
    price = format_price(product.get("price"))
    sale_price = product.get("salePrice")
    compare_price = product.get("comparePrice")
    # ShopWired uses 'active' (boolean) not 'status' (string)
    active = product.get("active")
    if active is True or active == 1:
        status = "Active"
    elif active is False or active == 0:
        status = "Hidden"
    else:
        status = "N/A"
    stock = product.get("stock", "N/A")
    url = product.get("url", "")
    description = product.get("description", "")

    lines = [
        f"📦 **{title}** (ID: {product_id})",
        f"   Price: {price}",
    ]
    if sale_price:
        lines.append(f"   Sale Price: {format_price(sale_price)}")
    if compare_price:
        lines.append(f"   Compare Price: {format_price(compare_price)}")
    if sku:
        lines.append(f"   SKU: {sku}")
    lines.append(f"   Stock: {stock}")
    lines.append(f"   Status: {status}")
    if url:
        lines.append(f"   URL: {url}")
    if description:
        # Truncate long descriptions
        desc_preview = description[:150].strip()
        if len(description) > 150:
            desc_preview += "..."
        lines.append(f"   Description: {desc_preview}")

    return "\n".join(lines)


def format_product_list(products: list[dict[str, Any]], total: int | None = None) -> str:
    """Format a list of products."""
    if not products:
        return "No products found."

    header = f"Found {total or len(products)} product(s):\n"
    formatted = [format_product(p) for p in products]
    return header + "\n\n".join(formatted)


def format_order(order: dict[str, Any]) -> str:
    """Format a single order for display."""
    order_id = order.get("id", "N/A")
    # Try common field names for order reference
    reference = order.get("reference", order.get("orderReference", ""))
    status = order.get("status", order.get("orderStatus", "N/A"))
    total = order.get("total", order.get("orderTotal", 0))
    currency = order.get("currency", "GBP")
    created = order.get("createdAt", order.get("dateCreated", order.get("created", "")))

    # Customer info - might be nested or flat
    customer = order.get("customer", {})
    if isinstance(customer, dict):
        customer_name = f"{customer.get('firstName', '')} {customer.get('lastName', '')}".strip()
        customer_email = customer.get("email", "")
    else:
        customer_name = order.get("customerName", order.get("firstName", ""))
        customer_email = order.get("customerEmail", order.get("email", ""))

    lines = [
        f"🛒 **Order #{order_id}**" + (f" ({reference})" if reference else ""),
        f"   Status: {status}",
        f"   Total: £{float(total or 0):.2f}" if total else "   Total: N/A",
    ]
    if customer_name:
        lines.append(f"   Customer: {customer_name}")
    if customer_email:
        lines.append(f"   Email: {customer_email}")
    if created:
        lines.append(f"   Created: {created}")

    return "\n".join(lines)


def format_order_list(orders: list[dict[str, Any]], total: int | None = None) -> str:
    """Format a list of orders."""
    if not orders:
        return "No orders found."

    header = f"Found {total or len(orders)} order(s):\n"
    formatted = [format_order(o) for o in orders]
    return header + "\n\n".join(formatted)


def format_customer(customer: dict[str, Any]) -> str:
    """Format a single customer for display."""
    customer_id = customer.get("id", "N/A")
    first_name = customer.get("firstName", customer.get("first_name", ""))
    last_name = customer.get("lastName", customer.get("last_name", ""))
    name = f"{first_name} {last_name}".strip() or "Unknown"
    email = customer.get("email", "N/A")
    phone = customer.get("phone", customer.get("telephone", ""))
    company = customer.get("company", "")

    lines = [
        f"👤 **{name}** (ID: {customer_id})",
        f"   Email: {email}",
    ]
    if phone:
        lines.append(f"   Phone: {phone}")
    if company:
        lines.append(f"   Company: {company}")

    return "\n".join(lines)


def format_customer_list(customers: list[dict[str, Any]], total: int | None = None) -> str:
    """Format a list of customers."""
    if not customers:
        return "No customers found."

    header = f"Found {total or len(customers)} customer(s):\n"
    formatted = [format_customer(c) for c in customers]
    return header + "\n\n".join(formatted)


def format_category(category: dict[str, Any]) -> str:
    """Format a single category."""
    cat_id = category.get("id", "N/A")
    name = category.get("name", category.get("title", "Unnamed"))
    description = category.get("description", "")
    parent_id = category.get("parentId", category.get("parent_id", ""))

    lines = [f"📁 **{name}** (ID: {cat_id})"]
    if parent_id:
        lines.append(f"   Parent ID: {parent_id}")
    if description:
        desc_preview = description[:100].strip()
        if len(description) > 100:
            desc_preview += "..."
        lines.append(f"   Description: {desc_preview}")

    return "\n".join(lines)


def format_voucher(voucher: dict[str, Any]) -> str:
    """Format a single voucher."""
    voucher_id = voucher.get("id", "N/A")
    code = voucher.get("code", "N/A")
    voucher_type = voucher.get("type", voucher.get("voucherType", "N/A"))
    value = voucher.get("value", voucher.get("amount", 0))
    active = voucher.get("active", None)

    status = "Active" if active else "Inactive" if active is not None else "N/A"

    lines = [
        f"🎟️ **{code}** (ID: {voucher_id})",
        f"   Type: {voucher_type}",
        f"   Value: {value}",
        f"   Status: {status}",
    ]
    return "\n".join(lines)


def format_generic_list(items: list[dict[str, Any]], item_type: str = "item") -> str:
    """Format a generic list of items."""
    if not items:
        return f"No {item_type}s found."

    lines = [f"Found {len(items)} {item_type}(s):\n"]
    for item in items:
        item_id = item.get("id", "N/A")
        name = item.get("name", item.get("title", item.get("code", f"{item_type} {item_id}")))
        lines.append(f"  • {name} (ID: {item_id})")

    return "\n".join(lines)
