---
name: order-lifecycle-management
description: "Manage ShopWired order workflows end-to-end — status transitions, customer communications, fulfillment tracking, returns, and escalation logic. Use whenever the user asks about orders, order status, fulfillment, shipping updates, customer order queries, returns, refunds, order comments, or any order-related operation on a ShopWired store. Also trigger on 'what orders need attention', 'pending orders', 'order backlog', or any triage of order state."
---

# Order Lifecycle Management

Orders are the highest-volume, highest-risk operations in any e-commerce store. An agent that mishandles order status — marking something shipped when it hasn't left the warehouse, or triggering a premature refund — creates real business damage and erodes customer trust.

This skill defines the decision logic for every order operation on ShopWired: what you can do autonomously, what requires human confirmation, and what you should never do.

## ShopWired Order Data Model

An order in ShopWired contains:
- Order ID, status, dates
- Customer info (name, email, addresses)
- Line items (products, quantities, prices — remember prices are in pence)
- Payment and shipping details
- Admin comments (internal notes, not visible to customer)

Available tools:
- `list_orders` — Browse orders with optional status filter and pagination
- `get_order` — Full details for a specific order
- `search_orders` — Find orders by keyword (matches ID, customer name, email)
- `get_order_count` — Total orders, optionally filtered by status
- `update_order_status` — Change status, optionally notify customer
- `add_order_comment` — Add internal admin note
- `delete_order` — Permanent deletion (requires confirmation flag)

## Order Status Transition Rules

### Safe Autonomous Actions (no human confirmation needed)

These are read-only or low-risk operations the agent can perform freely:

- **Querying order details**: `get_order`, `search_orders`, `list_orders`
- **Counting orders**: `get_order_count`
- **Adding admin comments**: `add_order_comment` — internal notes are safe because they don't affect the customer or order state
- **Reporting on order status**: Summarizing order state, identifying patterns

### Actions Requiring Human Confirmation

Always ask the user before performing these:

- **Status changes**: `update_order_status` — Confirm the new status and whether to notify the customer
  - "I found order #1234 currently in 'processing'. Should I update it to 'shipped' and notify the customer?"
  - Never batch-update statuses without explicit approval for the batch

- **Customer notifications**: The `notify_customer` parameter on `update_order_status` sends an email. Always confirm:
  - "Should I send the customer an email about this status change?"
  - Default to `notify_customer: false` unless the user specifically requests notification

### Prohibited Actions

- **Deleting orders**: While the API supports `delete_order`, this is permanent and irreversible. Always advise the user to perform deletions themselves. Explain that deleted orders cannot be recovered.
- **Bulk status changes without review**: Never update more than one order's status without showing the user the full list first.

## Order Triage: "What Needs Attention?"

When a user asks what orders need attention, run this triage sequence:

### Step 1: Get the lay of the land
```
Call: get_order_count (no filter) — total orders
Call: get_order_count (status: 'pending') — awaiting action
Call: get_order_count (status: 'processing') — in progress
```

### Step 2: Surface the pending orders
```
Call: list_orders (status: 'pending', count: 50)
```

### Step 3: Identify outliers
Look for:
- Orders that have been in 'pending' for more than 48 hours (check dates)
- Orders with unusually high values (could indicate B2B or wholesale)
- Orders from repeat customers (check customer info across orders)

### Step 4: Present a prioritized summary
Don't dump raw data. Present:
1. **Urgent**: Orders stuck in pending that should have moved
2. **Ready to ship**: Orders in processing that may be ready for fulfillment
3. **FYI**: Recently completed orders, overall volume trends

## Customer Order Queries

When a customer (or user acting on behalf of a customer) asks about an order:

1. **Find the order**: Use `search_orders` with customer name, email, or order ID
2. **Present relevant info**: Status, expected timeline, tracking (if in order details)
3. **Don't expose internal notes**: Admin comments are internal — never share them with customers
4. **Suggest next steps**: If the order is delayed, suggest the user contact the customer proactively

## Fulfillment Workflow

For a typical order lifecycle:

```
pending → processing → shipped → completed
```

The agent's role at each stage:

- **Pending → Processing**: "This order is ready to be picked and packed. Should I update the status to processing?"
- **Processing → Shipped**: "Has this order been dispatched? If so, I'll mark it as shipped." Always ask — the agent can't verify physical shipment.
- **Shipped → Completed**: "The customer has received the order. Should I mark it as completed?"

For non-standard status values: ShopWired allows custom statuses. If you encounter unfamiliar statuses, report them to the user rather than assuming their meaning.

## Returns and Refund Handling

ShopWired's API does not have dedicated refund endpoints in the MCP toolset. When a return or refund situation arises:

1. **Document it**: Use `add_order_comment` to log the return request with details
2. **Update status**: Suggest updating order status to indicate the return (e.g., 'returned' if the store uses that status)
3. **Escalate to human**: Refund processing must be done through ShopWired's admin interface or payment provider. Tell the user: "I've logged the return request on the order. You'll need to process the refund through your ShopWired admin panel or payment provider directly."

Never promise a customer that a refund has been issued unless you can verify it through the system.

## Communication Templates

When suggesting customer-facing messages, keep them professional but warm:

**Order shipped notification context:**
> "Order #{id} has been shipped. The customer will receive an automatic email if you confirm notification."

**Delayed order (for the user to send):**
> "Suggest reaching out to the customer about order #{id} — it's been in processing for {days} days. Would you like me to draft a message?"

Always frame these as suggestions for the user, not actions the agent takes directly.
