"""Customer management tools for ShopWired MCP server."""

from shopwired_mcp.client import api_client
from shopwired_mcp.utils.formatting import format_customer, format_customer_list


async def list_customers(
    count: int = 50,
    offset: int = 0,
) -> str:
    """List customers from the store.

    Args:
        count: Number of customers per page (default: 50, max: 250)
        offset: Number of customers to skip for pagination (default: 0)
    """
    params: dict = {"count": min(count, 250)}
    if offset:
        params["offset"] = offset

    data = await api_client.get("customers", params=params)

    if isinstance(data, list):
        return format_customer_list(data)
    elif isinstance(data, dict) and "customers" in data:
        return format_customer_list(data["customers"], total=data.get("total"))
    return "No customers found."


async def get_customer(customer_id: int) -> str:
    """Get full details for a specific customer.

    Args:
        customer_id: The numeric customer ID
    """
    data = await api_client.get(f"customers/{customer_id}")
    return format_customer(data)


async def get_customer_count() -> str:
    """Get the total number of customers in the store."""
    data = await api_client.get("customers/count")

    if isinstance(data, dict):
        count = data.get("count", data.get("total", "unknown"))
        return f"Total customers: {count}"
    return f"Total customers: {data}"


async def create_customer(
    first_name: str,
    last_name: str,
    email: str,
    phone: str = "",
    company: str = "",
) -> str:
    """Create a new customer record.

    Args:
        first_name: Customer's first name (required)
        last_name: Customer's last name (required)
        email: Customer's email address (required)
        phone: Phone number
        company: Company name
    """
    payload: dict = {
        "firstName": first_name,
        "lastName": last_name,
        "email": email,
    }
    if phone:
        payload["phone"] = phone
    if company:
        payload["company"] = company

    data = await api_client.post("customers", json_data=payload)
    return f"Customer created successfully:\n{format_customer(data)}"
