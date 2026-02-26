"""Tests for response formatting utilities."""

from shopwired_mcp.utils.formatting import (
    format_customer,
    format_order,
    format_product,
    format_product_list,
)


def test_format_product_basic():
    product = {"name": "Test Widget", "id": 123, "price": 29.99, "sku": "TW-001"}
    result = format_product(product)
    assert "Test Widget" in result
    assert "123" in result
    assert "29.99" in result
    assert "TW-001" in result


def test_format_product_missing_fields():
    product = {"name": "Minimal"}
    result = format_product(product)
    assert "Minimal" in result
    assert "N/A" in result


def test_format_product_list_empty():
    assert format_product_list([]) == "No products found."


def test_format_product_list_with_items():
    products = [
        {"name": "Product A", "id": 1, "price": 10.0},
        {"name": "Product B", "id": 2, "price": 20.0},
    ]
    result = format_product_list(products)
    assert "Product A" in result
    assert "Product B" in result
    assert "2 product(s)" in result


def test_format_order_basic():
    order = {
        "id": 456,
        "status": "processing",
        "total": 99.50,
        "customer": {"first_name": "John", "last_name": "Doe", "email": "john@example.com"},
        "items": [{"name": "Widget", "quantity": 2, "price": 49.75}],
    }
    result = format_order(order)
    assert "456" in result
    assert "processing" in result
    assert "John Doe" in result
    assert "Widget" in result


def test_format_customer_basic():
    customer = {
        "id": 789,
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@example.com",
    }
    result = format_customer(customer)
    assert "Jane Smith" in result
    assert "jane@example.com" in result
