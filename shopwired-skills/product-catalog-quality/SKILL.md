---
name: product-catalog-quality
description: "Product catalog quality auditing and improvement for ShopWired stores. Scores product listings on data completeness, SEO readiness, image coverage, description quality, and variation consistency. Identifies weak listings that hurt conversion rates and channel eligibility. Use whenever the user asks about product quality, listing optimization, SEO, product descriptions, missing images, incomplete listings, catalog cleanup, 'which products need work', product data health, or any request to improve or audit product listings."
---

# Product Catalog Quality

A product listing is a conversion funnel compressed into a single page. Missing images, thin descriptions, absent weights, and inconsistent variation data don't just look unprofessional — they directly reduce conversion rates, hurt search rankings, and can disqualify products from external channels like Google Shopping.

This skill defines a systematic quality scoring framework for ShopWired product catalogs and provides actionable improvement recommendations.

## The Quality Scorecard

Every product is scored across 5 dimensions. Each dimension is scored 0-20 for a total quality score out of 100.

### Dimension 1: Title Quality (0-20 points)

| Criteria | Points |
|---|---|
| Title exists and is non-empty | 5 |
| Title length 30-80 characters (optimal for SEO and channels) | 5 |
| Title includes brand or product type keyword | 5 |
| Title avoids ALL CAPS, excessive punctuation, or promotional language ("SALE!", "BEST!!!") | 5 |

**How to check:**
```
Call: get_product(product_id)
→ Evaluate the title field against criteria
```

### Dimension 2: Description Quality (0-20 points)

| Criteria | Points |
|---|---|
| Description exists and is non-empty | 5 |
| Description length > 100 characters (not just a sentence fragment) | 5 |
| Description appears to contain actual product information (not placeholder text) | 5 |
| Description includes keywords relevant to the product category | 5 |

**Placeholder detection patterns:**
- "Lorem ipsum"
- "Description coming soon"
- "TBC", "TBD"
- Exact duplicate of another product's description
- Description identical to the title

### Dimension 3: Image Coverage (0-20 points)

| Criteria | Points |
|---|---|
| At least 1 image exists | 8 |
| At least 3 images exist (front, back, detail or in-use) | 6 |
| 5+ images (comprehensive visual coverage) | 6 |

**How to check:**
```
Call: list_product_images(product_id)
→ Count images returned
```

### Dimension 4: Data Completeness (0-20 points)

| Criteria | Points |
|---|---|
| SKU is set (not empty) | 5 |
| Price is set and > 0 | 5 |
| Weight is set (required for shipping calculations) | 5 |
| Stock value is set (not null) | 5 |

### Dimension 5: Variation Consistency (0-20 points)

For products without variations, auto-score 20/20.

For products with variations:

| Criteria | Points |
|---|---|
| All variations have stock values set | 5 |
| All variations have SKUs set | 5 |
| All variations have prices set (even if same as product-level) | 5 |
| Variation names are consistent format (not mixing "S" and "Small" and "small") | 5 |

**How to check:**
```
Call: list_product_variations(product_id)
→ Evaluate each variation against criteria
```

## Running a Catalog Audit

### Full Catalog Audit

When the user asks for a catalog quality review:

```
1. Call: get_product_count(active=true)
   → Determine scope

2. Call: list_products(active=true, count=50, offset=0)
   → Paginate through all active products

3. For each product:
   a. get_product(product_id) — title, description, price, SKU, weight
   b. list_product_images(product_id) — image count
   c. list_product_variations(product_id) — variation quality

4. Score each product on the 5 dimensions

5. Present results prioritized by worst scores first
```

### Audit Output Format

```
📊 Catalog Quality Report
Total products audited: {n}
Average quality score: {avg}/100

🔴 CRITICAL (Score < 40) — {count} products
These listings are likely hurting your store's performance:
- {Product A}: 25/100 — No images, no description, no SKU
- {Product B}: 30/100 — 1 image, placeholder description

⚠️ NEEDS WORK (Score 40-69) — {count} products
- {Product C}: 55/100 — Good description but only 1 image, missing weight
- {Product D}: 60/100 — Missing SKU, variations have inconsistent naming

✅ GOOD (Score 70-89) — {count} products
⭐ EXCELLENT (Score 90-100) — {count} products

Top 3 improvements with biggest impact:
1. Add images to {n} products (currently 0-1 images)
2. Write descriptions for {n} products (currently empty/placeholder)
3. Add SKUs to {n} products (needed for inventory tracking)
```

### Single Product Audit

When evaluating a specific product:

```
1. Score on all 5 dimensions
2. Show the breakdown:
   "Product: {name}
    Overall Score: {total}/100

    Title:        {x}/20  — {specific feedback}
    Description:  {x}/20  — {specific feedback}
    Images:       {x}/20  — {specific feedback}
    Data:         {x}/20  — {specific feedback}
    Variations:   {x}/20  — {specific feedback}

    Priority fix: {the lowest-scoring dimension with specific guidance}"
```

## SEO Readiness Assessment

Beyond internal quality, products need to be search-engine friendly:

### SEO Checklist Per Product
- **Title contains searchable keywords** — Would a customer search these words?
- **Description is unique** — Duplicate descriptions across products hurt SEO
- **Description length > 300 characters** — Thin content ranks poorly
- **Product has a category** — Uncategorized products are harder to index
- **Images exist** — Products without images rarely appear in image search or Google Shopping

### Google Shopping Eligibility

Google Shopping has strict product data requirements. Flag products that would fail:

- **Missing GTIN/EAN/UPC**: Google Shopping requires a product identifier for most categories
- **Missing brand**: Required for branded products
- **Missing weight**: Needed for shipping-rate calculations
- **Price = 0**: Will be rejected
- **No images**: Will be rejected
- **Description too short**: May be rejected or ranked poorly

Note: ShopWired's MCP API doesn't expose GTIN/EAN fields directly. Alert the merchant: "Google Shopping requires product identifiers (GTIN/EAN). These may need to be configured in your ShopWired admin panel directly."

## Improvement Recommendations

When suggesting improvements, prioritize by impact:

1. **Images** — Highest conversion impact. Products with 3+ images convert significantly better.
2. **Descriptions** — Second highest impact. Unique, detailed descriptions improve both SEO and conversion.
3. **SKUs** — Essential for inventory management and multi-channel sync.
4. **Weight** — Required for accurate shipping calculations.
5. **Variation consistency** — Prevents customer confusion and reduces support queries.

### Batch Improvement Planning

For catalogs with many low-quality listings, suggest a phased approach:

```
Phase 1 (This week): Fix the {n} critical products (score < 40)
- Add at least 1 image to each
- Write a 2-3 sentence description for each

Phase 2 (Next 2 weeks): Improve the {n} "needs work" products
- Add 2+ additional images
- Expand descriptions to 300+ characters
- Fill in missing SKUs

Phase 3 (Ongoing): Get all products to 80+
- Add 5th+ images for hero products
- Optimize titles for SEO
- Ensure variation naming consistency
```

## Integration with Other Skills

- **store-intelligence-core**: Read product data correctly (pence pricing, variation hierarchy) before scoring
- **multi-channel-sync-governance**: Quality issues that disqualify products from Google Shopping or eBay should be flagged as higher priority
- **inventory-decision-engine**: Products with good quality scores but zero stock represent wasted effort — coordinate with inventory status
