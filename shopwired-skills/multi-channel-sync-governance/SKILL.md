---
name: multi-channel-sync-governance
description: "Multi-channel listing governance for ShopWired stores selling across eBay, Etsy, Google Shopping, Facebook, and Instagram. Handles sync delay awareness, channel-specific listing rules, cross-channel inventory conflict prevention, and deactivation cascade logic. Use whenever the user mentions eBay, Etsy, Amazon, Google Shopping, Facebook Shop, Instagram Shopping, marketplace, multi-channel, channel sync, listing sync, or any situation where a product change in ShopWired may affect external channel listings. Also trigger on 'why is my product still showing on eBay' or similar cross-channel discrepancy questions."
---

# Multi-Channel Sync Governance

ShopWired integrates with eBay, Etsy, Google Shopping, Facebook, and Instagram. These integrations sync product data outbound — but they are not real-time. Changes in ShopWired propagate to channels on a delay, and the agent has no direct control over the external channel listings.

This creates a dangerous gap: the agent can modify a product in ShopWired, but the old version persists on external channels for minutes to hours. Without understanding this, an agent might deactivate a sold-out product in ShopWired and tell the merchant "it's handled" — while the product remains purchasable on eBay for another 30 minutes.

## The Sync Model

### What ShopWired Controls
- Product data (title, description, price, images, stock, active status)
- These fields sync outbound to connected channels

### What ShopWired Does NOT Control
- Channel-specific listing details (eBay item specifics, Etsy tags, Google product categories)
- Channel listing status independent of ShopWired (eBay can end a listing for policy violations)
- Sync timing — the agent cannot force or accelerate a sync
- Channel-specific customer interactions (eBay messages, Etsy convos)

### Sync Delay Reality

The agent must always communicate sync delays when making changes that affect multi-channel listings:

| Action in ShopWired | Typical Sync Delay | Risk During Delay |
|---|---|---|
| Price change | 5-30 minutes | Customer buys at old price on external channel |
| Stock update | 5-30 minutes | Overselling on external channel |
| Product deactivation | 15-60 minutes | Product still purchasable on channel |
| New product activation | 15-60 minutes | Product not yet visible on channel |
| Image/description update | 15-60 minutes | Stale content on channel |

These are estimates. Actual delays depend on the channel, time of day, and sync queue depth.

## Decision Framework: Channel-Aware Actions

### Before Any Product Modification

Ask: "Is this product listed on any external channels?"

The ShopWired MCP tools don't directly report which channels a product is syndicated to. The agent must:

1. Ask the merchant: "Is this product listed on eBay, Etsy, or other channels?"
2. If yes, warn about sync delays before making changes
3. If unknown, assume multi-channel and warn conservatively

### Price Changes

**Safe approach:**
1. Confirm with merchant: "I'll update the price to £X.XX in ShopWired. If this product is on eBay/Etsy, the old price will remain active for up to 30 minutes. Should I proceed?"
2. After updating: "Price updated in ShopWired. Monitor your external channels — the change should propagate within 30 minutes."

**Dangerous pattern to avoid:**
- Changing price during a flash sale and assuming it's live everywhere immediately
- Reducing price on ShopWired while a higher-priced listing persists on eBay (could trigger eBay's duplicate listing policies)

### Stock Changes (Including Zero-Stock)

This is the highest-risk multi-channel scenario:

**When stock hits zero:**
1. Update stock in ShopWired: `update_stock(product_id, 0)`
2. Immediately warn: "⚠️ Stock is now zero in ShopWired. If this product is listed on eBay/Etsy/Google Shopping, it may still appear available for up to 30 minutes. During this window, customers could place orders you can't fulfill."
3. Suggest manual action: "For immediate removal, you may want to manually end the listing on [channel] directly while the sync catches up."

**When restocking after zero:**
1. Update stock in ShopWired first
2. Warn: "Stock updated to {quantity} in ShopWired. External channel listings will reflect the new stock within 15-30 minutes. Orders may not flow in from channels until the sync completes."

### Product Deactivation/Activation

**Deactivating a product:**
```
1. Confirm with user: "Deactivating {product_name} in ShopWired.
   Channel sync warning: This product may remain visible and purchasable
   on external channels for up to 60 minutes."
2. Call: update_product(product_id, active=false)
3. Follow-up: "Product deactivated in ShopWired. Recommended: check your
   [eBay/Etsy] dashboard to confirm the listing ends within the hour."
```

**Reactivating a product:**
```
1. Verify stock is available (use inventory-decision-engine)
2. Verify price is current
3. Call: update_product(product_id, active=true)
4. Warn: "Product is now active in ShopWired. It may take 15-60 minutes
   to reappear on external channels."
```

## Channel-Specific Awareness

### eBay Integration
- eBay has strict listing policies — price changes that are too frequent can flag the listing
- eBay "sold" history is visible to buyers — sudden price drops after sales can erode trust
- eBay listings have their own category requirements that ShopWired data may not satisfy
- If a product is deactivated in ShopWired, the eBay listing ends — but "ended" listings remain visible in search for a period

### Etsy Integration
- Etsy has different inventory semantics (quantity vs. variations)
- Etsy listings can be "sold out" but still visible with a "notify me" option
- Etsy SEO is heavily tag-dependent — changes to ShopWired product titles may not update Etsy tags
- Etsy charges listing fees — reactivating a product may incur a new listing fee on Etsy

### Google Shopping
- Google Merchant Center has strict product data requirements (GTIN, MPN, brand)
- Products disappearing and reappearing can affect Google Shopping quality score
- Price discrepancies between ShopWired and Google Shopping can cause disapprovals

### Facebook/Instagram Shopping
- Facebook Catalog syncs from ShopWired product feed
- Catalog review can take 24-48 hours for new products
- Deactivated products are removed from the catalog but tagged posts may persist

## Conflict Prevention Patterns

### Pattern 1: The Oversell Cascade
Scenario: Product has 2 units. One sells on website, one sells on eBay — but the sync hasn't updated eBay yet, so a third customer buys on eBay.

Prevention:
- When stock is low (≤5 units) on a multi-channel product, proactively warn: "This product has only {n} units and is listed on multiple channels. There's a risk of overselling during sync delays."
- Suggest buffer stock: "Consider reserving 1-2 units as a buffer for sync delays."

### Pattern 2: The Price War
Scenario: Merchant runs a 20% off sale in ShopWired. eBay listing still shows full price for 30 minutes. Customer sees both prices and loses trust.

Prevention:
- "If you're running a sale, consider updating external channel prices first (manually in each platform), then updating ShopWired — this way the lower price appears everywhere simultaneously."

### Pattern 3: The Ghost Listing
Scenario: Product is deleted from ShopWired but the eBay/Etsy listing persists because the sync only handles deactivation, not deletion.

Prevention:
- "Deleting a product from ShopWired may not remove it from all channels. Recommend deactivating first, verifying channel listings are removed, then deleting."

## Integration with Other Skills

- **inventory-decision-engine**: When stock levels trigger an "Act" or "Escalate" decision, always check multi-channel exposure before recommending deactivation
- **pricing-promotion-guard**: Price changes must be evaluated for multi-channel impact before execution
- **store-intelligence-core**: The standard audit should include asking the merchant which channels they're active on — this context is critical for every subsequent decision
