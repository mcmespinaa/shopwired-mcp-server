---
name: b2b-wholesale-routing
description: "B2B and wholesale order intelligence for ShopWired stores. Detects wholesale vs retail context from order patterns, customer data, and order values. Applies tiered pricing logic, trade account handling, minimum order enforcement, and B2B-specific communication. Use whenever the user mentions wholesale, trade accounts, bulk orders, B2B customers, tiered pricing, volume discounts, trade pricing, minimum order quantities, or when an order value or quantity pattern suggests wholesale activity."
---

# B2B Wholesale Routing

Most ShopWired stores serve both retail (B2C) and wholesale (B2B) customers through the same storefront. The challenge is that ShopWired's API doesn't have a native "customer type" field — there's no `is_wholesale: true` flag. The agent has to infer B2B context from signals, then apply the right business logic.

Getting this wrong means either: giving retail customers wholesale pricing (margin erosion), or treating wholesale customers like retail browsers (losing high-value accounts).

## Detecting B2B vs B2C Context

### Signal-Based Classification

Since ShopWired doesn't tag customers as wholesale/retail, use these signals:

**Strong B2B indicators:**
- Order value > £500 (50000 pence) — especially on first order
- Quantity of single SKU > 10 units
- Customer has "Ltd", "LLC", "Inc", "GmbH", "Trading", "Wholesale", "Distribution" in name or company field
- Repeat orders with consistent high volumes
- Customer email uses a company domain (not gmail/hotmail/yahoo)

**Weak B2B indicators (need corroboration):**
- Order placed during business hours on weekdays
- Shipping address is a commercial/industrial zone
- Customer has placed more than 3 orders

**Retail indicators:**
- Single-unit purchases across mixed categories
- Consumer email domains
- Gift wrapping or personal messages in order notes
- Shipping to residential addresses

### Classification Sequence

```
1. Call: get_customer(customer_id)
   → Check company field, email domain, name patterns

2. Call: search_orders(query=customer_email)
   → Pull order history, calculate average order value and frequency

3. Apply signal scoring:
   - Strong B2B signal = +3 points
   - Weak B2B signal = +1 point
   - Retail indicator = -2 points
   - Score ≥ 5 = likely B2B
   - Score 2-4 = ambiguous, ask the merchant
   - Score < 2 = likely B2C
```

Always present the classification as a recommendation, not a fact:
- "Based on order patterns, this looks like a B2B customer — average order value of £1,200 across 5 orders, company domain email, and 'Trading Ltd' in their name. Want me to treat them as wholesale?"

## Tiered Pricing Logic

ShopWired doesn't have native price tiers. Wholesale pricing is typically managed through:

1. **Voucher codes** — A dedicated wholesale discount code
2. **Separate products** — Wholesale-only product listings (often hidden from main storefront)
3. **Manual price overrides** — The merchant adjusts prices per order

### When the User Asks About Wholesale Pricing

```
1. Call: list_vouchers
   → Check for wholesale/trade-specific voucher codes

2. Call: search_products(query="wholesale") or search_products(query="trade")
   → Check if separate wholesale product listings exist

3. Report findings to user:
   - "You have a voucher code 'TRADE20' giving 20% off. Is this your wholesale pricing mechanism?"
   - "I found 15 products with 'wholesale' in the title. Are these your B2B listings?"
```

### Pricing Guard Rails

When processing what appears to be a wholesale order:

- **Never auto-apply discounts** — Even if a wholesale voucher exists, confirm with the merchant before applying
- **Flag unusual discount stacking** — If a wholesale customer also uses a promotional code, alert: "This order has both the TRADE20 wholesale discount and the SUMMER10 promo code applied. Combined discount is 28%. Is this intentional?"
- **Minimum order enforcement** — If the merchant has communicated minimum order values, check: "This wholesale order is £180 but your minimum is £250. Want me to flag this with the customer?"

## Trade Account Management

### New Trade Account Request

When a potential B2B customer contacts through the store:

1. **Gather information**: Company name, registration number, expected order volume, payment terms requested
2. **Create customer record**: `create_customer(first_name, last_name, email, company)`
3. **Add internal notes**: Use order comments on their first order to document trade terms
4. **Suggest follow-up**: "I've created the customer record. You'll need to manually set up any trade pricing arrangements in your ShopWired admin."

### Trade Account Review

When asked to review B2B customer health:

```
1. Call: list_customers with pagination
2. For each customer with B2B signals:
   - Pull order history via search_orders
   - Calculate: total revenue, order frequency, average order value
   - Flag: declining order frequency, long gaps between orders, shrinking order values
3. Present as a B2B customer health report
```

Format:
```
📊 B2B Customer Health

🟢 HEALTHY (ordering regularly, growing)
- Acme Trading Ltd: £12,400 total, 8 orders, avg £1,550, last order 5 days ago

⚠️ AT RISK (declining or irregular)
- Beta Wholesale: £8,200 total, 6 orders, avg £1,367, last order 45 days ago

🔴 DORMANT (no orders in 60+ days)
- Gamma Distribution: £3,100 total, 2 orders, avg £1,550, last order 92 days ago
```

## Bulk Order Processing

When processing orders that appear to be bulk/wholesale:

1. **Verify stock availability** across all items before confirming — use the inventory-decision-engine skill's variation-level stock checking
2. **Calculate total weight** for shipping implications
3. **Check if the order spans multiple categories** — B2B orders that span unrelated categories may indicate a reseller
4. **Flag to the merchant** for manual review if the order value exceeds £2,000 — high-value orders deserve human attention

## Integration with Other Skills

- **inventory-decision-engine**: B2B orders can drain stock rapidly. A single wholesale order might move a product from "healthy" to "critical". After processing a B2B order, re-run inventory checks on affected products.
- **pricing-promotion-guard**: Wholesale pricing and promotional discounts can stack in unexpected ways. Cross-reference before confirming any discounted wholesale order.
- **order-lifecycle-management**: B2B orders may have different fulfillment patterns (palletized shipping, split deliveries, pro-forma invoicing). Flag these for human handling.
