---
name: inventory-decision-engine
description: "Inventory monitoring, alerting, and action logic for ShopWired stores. Codifies threshold-based decisions: when to monitor silently, when to alert the merchant, when to auto-pause a listing, and when to escalate. Handles stock level interpretation, variation-level inventory, multi-channel conflict awareness, and backorder logic. Use whenever the user asks about stock levels, inventory management, low stock alerts, restocking, out-of-stock products, stock discrepancies, inventory health, or 'which products need restocking'. Also trigger on any stock update operation."
---

# Inventory Decision Engine

Most generic e-commerce agents handle inventory in one of two broken ways: they either do nothing (just report numbers) or they overreact (auto-hiding products at the first sign of low stock). Both are wrong.

This skill defines a threshold-based decision framework: Monitor → Alert → Act → Escalate. The right response depends on the product, the velocity, and the merchant's tolerance for stockouts.

## Reading Inventory Correctly

Before any inventory decision, read the store-intelligence-core skill's guidance on the product/variation hierarchy. The critical rule:

**If a product has variations, the product-level stock is unreliable. Always call `list_product_variations` and use variation-level stock as the source of truth.**

### Inventory Audit Sequence

1. **Get the product**: `get_product(product_id)`
2. **Check for variations**: `list_product_variations(product_id)`
3. **Calculate true stock**:
   - No variations → product-level `stock` is authoritative
   - Has variations → sum of variation-level `stock` values = true available stock
4. **Check active status**: A product with `active: false` and stock > 0 may be intentionally held back

## The Decision Framework

### Level 1: Monitor (No Action)

Stock is healthy. Log the state if asked, but don't alert.

Conditions:
- Stock > 20 units (or > 30 days of estimated supply based on recent order velocity)
- All variations have stock > 5 units each
- Product is active and selling normally

Agent behavior: Report numbers if asked. No proactive alerts.

### Level 2: Alert (Notify Merchant)

Stock is getting low. The merchant should know, but no automated action yet.

Conditions:
- Stock between 5-20 units (or 7-30 days of supply)
- Any single variation drops below 5 units
- Stock decreased by more than 50% since last check

Agent behavior:
- Proactively mention low stock when discussing related products
- "Heads up: {product_name} is down to {stock} units. The {variation} variant has only {var_stock} left."
- Suggest restocking but don't take action

### Level 3: Act (Propose Specific Action)

Stock is critically low. Propose a concrete action for the merchant to approve.

Conditions:
- Stock between 1-5 units
- Any variation at 0 units while others have stock
- High-velocity product (frequent orders) approaching zero

Agent behavior:
- "⚠️ {product_name} has only {stock} units left. At current sales velocity, this will stock out in approximately {days} days."
- Propose options: "Should I (a) deactivate this product to prevent overselling, or (b) leave it active while you restock?"
- If a variation is at 0: "The {variation} variant is out of stock. The product is still active because other variants have stock. Want me to add a comment noting which variant needs restock?"

### Level 4: Escalate (Urgent Human Decision)

Something is wrong that the agent cannot resolve alone.

Conditions:
- Stock is 0 across all variations but the product is still active
- Stock shows negative numbers (data integrity issue)
- Multiple products hit zero simultaneously (possible bulk issue)
- Stock numbers don't match between product and variation levels

Agent behavior:
- "🚨 {product_name} is at zero stock but still listed as active on your store. Customers can still see and attempt to purchase this product. This needs immediate attention."
- "I've found a discrepancy: the product shows {product_stock} units but the variations total {var_total}. This may indicate a sync issue."
- Never auto-fix data integrity issues. Report them and let the merchant decide.

## Stock Update Operations

When the user wants to update stock:

### Single Product Update
```
Call: update_stock(product_id, stock)
— or —
Call: update_stock(product_id, stock, variation_id)
```

Always confirm before updating:
- "I'll update {product_name} stock from {current} to {new_value}. Confirm?"
- For variations: "I'll update the {variation_name} variant of {product_name} from {current} to {new_value}. Confirm?"

### Bulk Stock Check

When asked "which products need restocking" or "show me low stock items":

1. Call `list_products(active=true)` with pagination to get all active products
2. For each product, check stock levels (including variation-level)
3. Categorize using the framework above (Monitor/Alert/Act/Escalate)
4. Present only the Alert, Act, and Escalate categories — don't waste the merchant's time with healthy products

Format the output as a prioritized list:
```
🚨 URGENT (Act Now)
- Product A: 0 units, still active
- Product B: 2 units remaining

⚠️ LOW STOCK (Plan Restock)
- Product C: 8 units, ~5 days supply
- Product D: "Blue" variant at 3 units
```

## Deactivation Logic

When a product should be temporarily hidden:

1. Confirm with the user: "Should I deactivate {product_name} to prevent overselling?"
2. If approved: `update_product(product_id, active=false)`
3. Add a comment or note explaining why it was deactivated
4. Remind the user to reactivate once restocked

Never auto-deactivate without user confirmation. The merchant may prefer to allow backorders or show "out of stock" messaging through their theme rather than hiding the product entirely.

## Multi-Channel Awareness

ShopWired integrates with eBay, Etsy, Google Shopping, Facebook, and Instagram. When discussing inventory:

- Stock changes in ShopWired may not immediately reflect on external channels
- If a product is sold out, it may still appear available on eBay/Etsy until the sync runs
- Alert the merchant to this delay: "Note: deactivating this product in ShopWired won't immediately remove it from your eBay/Etsy listings. There may be a sync delay."

This is where the multi-channel-sync-governance skill takes over for deeper channel management.
