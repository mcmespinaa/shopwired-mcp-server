"""Customer management MCP tools."""

from __future__ import annotations

import logging
import re
from typing import Any

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from ..client import api_client
from ..utils.formatting import format_customer, format_customer_list

logger = logging.getLogger(__name__)


def register_customer_tools(mcp: FastMCP) -> None:
    """Register all customer-related tools with the MCP server."""

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def list_customers(
        count: int = 50,
        offset: int = 0,
    ) -> str:
        """List customers from the store.

        Args:
            count: Number of customers per page (default: 50, max: 250)
            offset: Number of customers to skip for pagination (default: 0)
        """
        if count < 1:
            return "Count must be at least 1."
        if offset < 0:
            return "Offset cannot be negative."
        params: dict[str, Any] = {"count": min(count, 250)}
        if offset:
            params["offset"] = offset

        data = await api_client.get("/customers", params=params)

        if isinstance(data, list):
            return format_customer_list(data)
        elif isinstance(data, dict) and "customers" in data:
            return format_customer_list(data["customers"], total=data.get("total"))
        return "No customers found."

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def get_customer(customer_id: int) -> str:
        """Get full details for a specific customer.

        Args:
            customer_id: The numeric customer ID
        """
        if customer_id < 1:
            return "Invalid customer ID."
        data = await api_client.get(f"/customers/{customer_id}")
        customer = data.get("data", data) if isinstance(data, dict) else data
        return format_customer(customer)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def get_customer_count() -> str:
        """Get the total number of customers in the store."""
        data = await api_client.get("/customers/count")

        if isinstance(data, dict):
            count = data.get("count", data.get("total", "unknown"))
            return f"Total customers: {count}"
        return f"Total customers: {data}"

    @mcp.tool(annotations=ToolAnnotations(idempotentHint=False))
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
        if not first_name.strip():
            return "First name cannot be empty."
        if not last_name.strip():
            return "Last name cannot be empty."
        if not email.strip():
            return "Email cannot be empty."
        if not _EMAIL_RE.match(email):
            return "Invalid email address format."
        body: dict[str, Any] = {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
        }
        if phone:
            body["phone"] = phone
        if company:
            body["company"] = company

        data = await api_client.post("/customers", body)
        customer = data.get("data", data) if isinstance(data, dict) else data
        return f"Customer created successfully!\n\n{format_customer(customer)}"
