---
name: store-intelligence-core
description: "Foundational ShopWired store reading skill. Teaches agents how to correctly interpret ShopWired store state — product status, stock levels, variation hierarchies, category structure, and business configuration — before taking any action. Use this skill FIRST whenever working with a ShopWired store, before any other shopwired skill. Trigger on: any ShopWired store interaction, store audit, store health check, 'what's in my store', 'show me my products', store overview, onboarding a new ShopWired store, or any time you need to understand store state before acting."
---

# Store Intelligence Core

This is the foundation skill for ShopWired agent interactions. Every other ShopWired skill depends on this one. Before modifying anything in a ShopWired store — products, orders, inventory, pricing — you must first understand how to read the store's state correctly.

ShopWired's data model has quirks that differ from Shopify, WooCommerce, and other platforms. Getting these wrong leads to silent failures: products that appear available but aren't, orders that look fulfilled but have pending items, inventory numbers that don't mean what you think they mean.

## The ShopWired Data Model

### Products: The Core Hierarchy

A ShopWired product is not a flat record. It's a hierarchy:

```
Product (top level)
├── Title, description, price, SKU, weight
├── Active status (true/false — controls visibility)
├── Stock level (at product level)
├── Variations (size, color, etc.)
│   ├── Each variation has its OWN stock level
│   ├── Each variation can have its OWN price
│   └── Each variation has its OWN SKU
└── Images (ordered list)
```

**The critical distinction**: When a product has variations, the product-level stock is NOT the total stock. Each variation tracks its own stock independently. If you call `get_product` and see `stock: 50` but the product has 3 color variations each with `stock: 10`, the actual available stock is 30 (sum of variations), not 50. The product-level stock field may be stale or represent a different concept.

**Always check for variations** before reporting stock levels:

1. Call `get_product` to get the product details
2. Call `list_product_variations` to check if variations exist
3. If variations exist, use variation-level stock as the source of truth
4. If no variations exist, the product-level stock is authoritative

### Product Status: Active vs. Inactive

ShopWired uses a simple boolean `active` field:
- `active: true` — Product is visible on the storefront and purchasable
- `active: false` — Product is hidden from customers but still exists in the system

There is no "draft" status in ShopWired's API. A product either exists and is active, or exists and is hidden. This matters because:
- You cannot "soft launch" a product — it's either live or not
- Deactivating a product does NOT remove it from any channel integrations automatically
- Reactivating a product makes it immediately visible — there's no review step

### Categories and Brands

Categories in ShopWired support nesting (parent/child relationships via `parent_id`). Products can belong to multiple categories. Brands are flat (no hierarchy).

When auditing store structure:
1. Call `list_categories` to understand the taxonomy
2. Call `list_brands` to understand brand organization
3. Call `list_products` with pagination to get a full product inventory

### Prices: Pence, Not Pounds

**ShopWired stores prices in pence (or the smallest currency unit).** A product priced at £99.99 is stored as `9999`. A product at £1,250.00 is stored as `125000`.

Always convert when presenting prices to users:
- API value `9999` → display as £99.99
- API value `500` → display as £5.00
- When creating/updating products, convert the user's price to pence: £49.99 → `4999`

## Reading Store State: The Standard Audit

When a user asks you to understand their store, perform this sequence:

### Step 1: Business Context
```
Call: get_business_details
Purpose: Understand the store name, location, contact info
```

### Step 2: Catalog Overview
```
Call: get_product_count (active=true) AND get_product_count (active=false)
Purpose: How many products are live vs. hidden
```

### Step 3: Category Structure
```
Call: list_categories
Purpose: Understand how products are organized
```

### Step 4: Order Volume
```
Call: get_order_count
Purpose: Understand business activity level
```

### Step 5: Customer Base
```
Call: get_customer_count
Purpose: Understand customer base size
```

### Step 6: Configuration
```
Call: list_payment_methods, list_shipping_zones, list_vouchers
Purpose: Understand operational setup
```

Present this as a coherent store profile, not a raw data dump. The user wants to understand their business state, not see API responses.

## Common Misreadings to Avoid

1. **"This product has no stock"** — Check variations first. The product-level stock might be 0 while variations have plenty.

2. **"This product is deleted"** — ShopWired's `active: false` means hidden, not deleted. Only `delete_product` actually removes a product.

3. **"The store has 50 products"** — That's the count from one page. Use `get_product_count` for the true total, or paginate through `list_products` with offset.

4. **"This order is complete"** — Order status in ShopWired is a string field. Common values include 'pending', 'processing', 'shipped', 'completed', but the store may use custom statuses. Don't assume what statuses mean without checking the store's conventions.

5. **"The price is 9999"** — That's pence. Present it as £99.99 (or the appropriate currency).

## When to Use This Skill

Use this skill as a prerequisite read before invoking any other ShopWired skill. Think of it as the "boot sequence" — you read store state correctly first, then act. If you skip this and go straight to modifying orders or inventory, you risk acting on misunderstood data.
