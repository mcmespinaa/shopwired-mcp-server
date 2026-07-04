---
name: pricing-promotion-guard
description: "Pricing and promotion safety layer for ShopWired stores. Prevents margin erosion from discount stacking, validates promotion logic before execution, enforces pricing consistency across product/variation hierarchies, and guards against common pricing mistakes. Use whenever the user mentions discounts, vouchers, promotions, sales, pricing changes, discount codes, coupon codes, flash sales, clearance, price updates, bulk pricing changes, BOGOF, free shipping offers, or any operation that modifies product prices or creates/edits voucher codes. Also trigger on 'create a discount', 'run a sale', or 'change prices'."
---

# Pricing & Promotion Guard

Pricing errors are the most expensive mistakes an e-commerce agent can make. A misplaced decimal turns a £99.99 product into £9.99. A stacking discount gives 50% off on top of 30% off. A bulk price update applies to the wrong product set. Unlike inventory errors (which can be corrected by restocking), pricing errors result in immediate, irreversible financial damage when customers complete purchases.

This skill defines the safety logic for every pricing and promotion operation.

## ShopWired Pricing Fundamentals

### Prices Are in Pence

This is the single most important rule, inherited from store-intelligence-core:
- API value `9999` = £99.99
- API value `500` = £5.00
- When the user says "set the price to £49.99" → convert to `4999`
- When reporting a price of `12500` → display as £125.00

**The decimal trap**: If a user says "set price to 49.99" without specifying the currency unit, confirm: "Just to confirm — you want the price set to £49.99 (which is 4999 in the system), not £4,999.00?"

### Variation-Level Pricing

Products with variations can have different prices per variation:
- A t-shirt might be £19.99 in S/M/L but £24.99 in XL/XXL
- Each variation's price is independent of the product-level price

Before any price change:
1. `get_product(product_id)` — get product-level price
2. `list_product_variations(product_id)` — check if variations have independent prices
3. If variations exist, clarify with the user: "This product has {n} variations with different prices. Should I update all variations, or just specific ones?"

## Price Change Safety Protocol

### Single Product Price Update

```
1. Get current state:
   - Call: get_product(product_id)
   - Call: list_product_variations(product_id)

2. Calculate the change:
   - Current: £{current_price}
   - Proposed: £{new_price}
   - Change: {percentage}% {increase/decrease}

3. Apply safety checks:
   - Price decrease > 50%? → Warning: "This is a {X}% price reduction. Confirm this isn't a data entry error?"
   - Price increase > 100%? → Warning: "This is a {X}% price increase. Confirm this is intentional?"
   - New price = 0? → Block: "Setting price to zero would make this product free. Did you mean to deactivate it instead?"
   - New price < 100 (£1.00)? → Warning: "This would price the product at £{price}. Is this a penny/pound confusion?"

4. Confirm with user:
   "I'll update {product_name} from £{current} to £{new}. This is a {X}% {increase/decrease}. Confirm?"

5. Execute: update_product(product_id, price=new_price_in_pence)
```

### Bulk Price Changes

When the user wants to change prices across multiple products:

**Never execute bulk price changes in a single step.** Instead:

1. **Preview first**: List all affected products with current and proposed prices
2. **Show the impact**: Total revenue impact if all products sell one unit at old vs new price
3. **Get explicit confirmation**: "This will change prices on {n} products. Here's the full list: [table]. Confirm?"
4. **Execute sequentially**: Update one at a time, logging each change
5. **Report results**: "Updated {n} products. Here's what changed: [summary]"

## Voucher & Discount Code Management

### Creating a Voucher

Available voucher types in ShopWired:
- `percentage` — e.g., 10% off
- `fixed` — e.g., £5 off
- `free_shipping` — waives shipping cost

```
Call: create_voucher(
  code="SUMMER10",
  voucher_type="percentage",
  value=10,
  active=true,
  min_order_value=2000,    // £20.00 minimum
  usage_limit=100,
  expiry_date="2026-06-30"
)
```

### Voucher Creation Safety Checks

Before creating any voucher:

1. **Check for existing similar codes**: `list_vouchers()` — look for codes with similar names or values that might cause confusion
2. **Validate the economics**:
   - Percentage discount > 30%? → Warning: "A {X}% discount is aggressive. Confirm this margin impact is acceptable?"
   - No minimum order value? → Warning: "This discount has no minimum order value. A customer could use it on any order, even £1. Should we set a minimum?"
   - No usage limit? → Warning: "This voucher has unlimited uses. Should we cap it?"
   - No expiry date? → Warning: "This voucher never expires. Should we set an end date?"
3. **Check for stacking potential**: If other active vouchers exist, warn about potential stacking

### Discount Stacking Detection

ShopWired may allow multiple discounts to apply to a single order. The agent must watch for:

**Dangerous stacking patterns:**
- Percentage voucher + percentage voucher = compound discount
- Fixed discount + free shipping = double benefit
- Wholesale pricing (via voucher) + promotional voucher = margin erosion

**Detection sequence:**
```
1. Call: list_vouchers
2. Count active vouchers
3. Check for overlapping conditions:
   - Multiple active percentage discounts
   - Vouchers with no minimum order value
   - Vouchers with no usage limit AND no expiry
4. Alert the merchant:
   "You have {n} active discount codes. Customers could potentially
   combine TRADE20 (20% off) with SUMMER10 (10% off) for a
   compound 28% discount. Is this intended?"
```

### Voucher Audit

When asked to review promotions or "what discounts are active":

```
1. Call: list_vouchers
2. For each voucher, classify:
   - 🟢 CONTROLLED: Has expiry, usage limit, and minimum order
   - ⚠️ OPEN-ENDED: Missing one or more controls
   - 🔴 RISKY: No expiry AND no usage limit AND no minimum
3. Present the audit with recommendations
```

Format:
```
📊 Active Voucher Audit

🔴 RISKY — Needs Attention
- FRIENDS50: 50% off, no expiry, no usage limit, no minimum
  → Recommend: Add expiry date and usage cap immediately

⚠️ OPEN-ENDED — Review Recommended
- WELCOME10: 10% off, expires 2026-12-31, no usage limit
  → Recommend: Consider a usage cap to control exposure

🟢 CONTROLLED — Looks Good
- SUMMER5: £5 off, expires 2026-07-01, 200 uses max, £30 minimum
```

## Promotion Planning

When the user wants to run a sale or promotion:

### Pre-Launch Checklist

1. **Define scope**: Which products are included? All, a category, specific items?
2. **Set the discount**: Percentage or fixed? Applied via voucher code or price reduction?
3. **Set guardrails**: Start/end dates, usage limits, minimum order values
4. **Check inventory**: Do the sale products have sufficient stock? (Use inventory-decision-engine)
5. **Check multi-channel**: Will this sale apply across all channels? (Use multi-channel-sync-governance)
6. **Stacking check**: Can this sale discount stack with existing vouchers?

### Sale via Price Reduction vs. Voucher Code

Help the merchant choose the right mechanism:

**Price reduction** (changing the actual product price):
- Visible to all customers automatically
- Applies across all channels (after sync)
- Harder to reverse if done on many products
- No tracking of who used the discount

**Voucher code**:
- Only available to customers who know the code
- Can be shared selectively (email list, social media, wholesale customers)
- Easy to deactivate or limit
- Tracks usage automatically
- Does NOT automatically apply to channel listings

### Post-Promotion Cleanup

After a sale ends:
1. Deactivate the voucher: suggest the user delete or deactivate it
2. If prices were reduced, restore them: "The sale has ended. Here are the {n} products that need their prices restored. Want me to update them?"
3. Check for lingering effects: "Any orders placed in the last hour may have captured the sale price. Monitor for late submissions."

## Integration with Other Skills

- **store-intelligence-core**: Always read prices in pence, always check variation pricing before modifying
- **inventory-decision-engine**: Before running a sale, verify stock levels can handle increased demand
- **multi-channel-sync-governance**: Price changes have sync delay implications across channels
- **b2b-wholesale-routing**: Wholesale pricing and promotional discounts can stack — always cross-check
