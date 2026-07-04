---
name: reporting-and-insight-framing
description: "Data interpretation guardrails and report generation for ShopWired stores. Prevents misleading metrics, ensures statistical honesty, and frames insights with appropriate caveats. Generates revenue dashboards, inventory health reports, customer metrics summaries, and product performance analyses from ShopWired data. Covers common statistical pitfalls: small sample sizes, seasonal bias, survivorship bias, correlation-causation confusion, and vanity metrics. Use whenever the user asks for reports, dashboards, analytics, 'how is my store doing', store performance, revenue summary, sales report, monthly report, KPI dashboard, business review, data analysis, metrics overview, trend analysis, or 'give me the numbers'."
---

# Reporting and Insight Framing

This skill is not about making numbers look good. It's about making numbers tell the truth.

ShopWired gives you raw data — orders, products, customers, stock levels. Turning that into useful insight requires knowing what to measure, what to compare it against, and what caveats to attach. Most AI-generated reports fail at the third part.

Every number this skill produces comes with context. Every trend comes with a sample size. Every recommendation comes with a confidence qualifier.

## Prerequisites

Read the store-intelligence-core skill first. Critical: all monetary values from ShopWired are in pence. An order total of `9999` = £99.99. Getting this wrong invalidates your entire report.

## Data Collection Patterns

### Revenue Data Collection
```
1. Call: get_order_count() → total orders
2. Call: get_order_count(status="completed") → completed orders
3. Paginate: list_orders(count=50, offset=0) through all orders
4. For each order: get_order(order_id)
   → Extract: total (in pence), created date, status, line items
5. Convert all monetary values: API value ÷ 100 = £ amount
```

### Inventory Data Collection
```
1. Call: get_product_count() → total products
2. Call: get_product_count(active=true) → active products
3. Paginate: list_products(count=50, offset=0)
4. For products with variations: list_product_variations(product_id)
5. Use variation-level stock as source of truth (see inventory-decision-engine)
```

### Customer Data Collection
```
1. Call: get_customer_count() → total customers
2. Paginate: list_customers(count=50, offset=0)
3. Cross-reference with order data for purchase history
4. Apply RFM scoring from customer-segment-intelligence
```

## Report Types

### 1. Store Health Dashboard

The go-to report when a merchant asks "how is my store doing?"

```
## Store Health Dashboard
Generated: [date]
Period: [start] to [end]
Data Confidence: [HIGH/MEDIUM/LOW — see confidence rules below]

### Revenue Summary
- Total Revenue: £X,XXX.XX ([N] completed orders)
- Average Order Value: £XX.XX
- Period-over-Period Change: [+/-X%] ⚠️ [caveat if sample < 30 orders]

### Order Pipeline
- Pending: [N]
- Processing: [N]
- Shipped: [N]
- Completed: [N]
- Cancelled: [N] ([X%] cancellation rate)

### Inventory Health
- Total Active Products: [N]
- Out of Stock: [N] (🔴 [X%] of catalogue)
- Low Stock (< 5 units): [N] (⚠️ [X%])
- Healthy Stock (5+ units): [N] (✅ [X%])

### Customer Overview
- Total Customers: [N]
- New This Period: [N]
- Repeat Buyers: [N] ([X%] repeat rate)

### ⚠️ Flags
[List any urgent issues: high cancellation rate, many OOS products, etc.]
```

### 2. Product Performance Report

Ranks products by revenue contribution.

```
## Product Performance Report
Period: [start] to [end]

### Top 10 Products by Revenue
| Rank | Product | Units Sold | Revenue | % of Total | Stock Remaining |
|------|---------|------------|---------|------------|-----------------|
| 1 | [name] | [N] | £X | X% | [N] |
...

### Bottom Performers (active products with zero sales in period)
| Product | Days Listed | Stock Level | Price | Quality Score |
|---------|-------------|-------------|-------|---------------|
...

### Concentration Risk
- Top product accounts for [X%] of revenue
  [⚠️ Flag if >30%: "Revenue is concentrated. If [product] goes
  out of stock or demand drops, it will significantly impact total revenue."]
- Top 5 products account for [X%] of revenue

### ⚠️ Interpretation Notes
- Products listed for less than 30 days are excluded from "bottom performers"
- Revenue is from completed orders only (excludes pending, cancelled, refunded)
- [If period < 30 days: "Short reporting period. Trends may not be representative."]
```

### 3. Inventory Risk Report

Combines stock data with sales velocity to flag risk.

```
## Inventory Risk Report
Generated: [date]

### 🔴 Critical (out of stock + had sales in last 30 days)
| Product | Last Sale | Units Sold (30d) | Est. Daily Demand | Days OOS |
|---------|-----------|------------------|-------------------|----------|
...

### ⚠️ At Risk (stock covers < 14 days at current sell rate)
| Product | Current Stock | Daily Sell Rate | Days Until OOS |
|---------|---------------|-----------------|----------------|
...

### ✅ Healthy
[Count] products have sufficient stock for 14+ days

### ℹ️ Methodology
- Daily sell rate = units sold in last 30 days ÷ 30
- "Days Until OOS" = current stock ÷ daily sell rate
- Products with zero sales in the last 30 days are excluded from velocity calculations
- [If fewer than 30 days of data available: "Sell rate estimates use [N] days
  of data and may be less reliable"]
```

### 4. Customer Health Report

Uses segments from customer-segment-intelligence.

```
## Customer Health Report
Period: [start] to [end]

### Segment Distribution
[Use format from customer-segment-intelligence audit output]

### Key Metrics
- Customer Acquisition Cost: [Cannot calculate — ShopWired doesn't track marketing spend]
- Repeat Purchase Rate: [X%] ([N] of [M] customers with 2+ orders)
- Average Customer Lifetime Value: £X
  ⚠️ [Caveat: LTV is calculated from available order history only.
  Customers who also buy through other channels are undercounted.]

### Retention Curve
| Cohort (First Purchase) | Total | Purchased Again in 30d | 60d | 90d | 180d |
|-------------------------|-------|------------------------|-----|-----|------|
...

### ⚠️ Data Limitations
- ShopWired doesn't track customer acquisition source
- Email engagement (opens, clicks) is not available through the API
- Customers who purchase as guests may appear as separate records
```

## Statistical Guardrails

These rules are non-negotiable. Every report must follow them.

### 1. Sample Size Honesty

**Rule**: Never state a trend or percentage without the underlying count.

- ❌ "Sales increased 200% this month"
- ✅ "Sales increased 200% this month (from 3 orders to 9 orders). With this small sample, the trend is not yet reliable."

Confidence thresholds:
- **HIGH confidence**: 100+ data points for the metric
- **MEDIUM confidence**: 30-99 data points — state the count, note limited reliability
- **LOW confidence**: Under 30 data points — present as directional only, not conclusive

### 2. Period-over-Period Comparison Rules

**Rule**: Never compare periods of different lengths or with known anomalies without flagging it.

- ❌ "Revenue is down 40% compared to December" (comparing January to peak holiday season)
- ✅ "Revenue decreased 40% vs December. Note: December typically includes holiday spending. A fairer comparison is January vs the prior January, or vs a non-seasonal month."

When making comparisons:
- Same-length periods only (month vs month, week vs week)
- Flag seasonal comparisons: December, Black Friday/Cyber Monday, Valentine's, school seasons
- If the store has less than 12 months of data, you cannot make year-over-year comparisons — say so

### 3. Survivorship Bias Prevention

**Rule**: Don't ignore the products that were removed or went out of stock.

- ❌ "Average product rating is 4.5 stars" (only counting products still active)
- ✅ "Average rating for currently active products is 4.5 stars. [N] products were deactivated during this period and are excluded from this average."

When analysing product performance:
- Acknowledge products that were deleted or deactivated during the period
- Note if "best sellers" analysis only includes currently active products
- Flag if stock-outs removed products from effective selling time

### 4. Correlation ≠ Causation

**Rule**: Never imply that a price change or promotion caused a sales change without controlling for other factors.

- ❌ "The 20% discount increased sales by 50%"
- ✅ "Sales increased 50% during the period when the 20% discount was active. Other factors that may have contributed: [seasonal timing, stock availability changes, new products added]. We cannot isolate the discount's impact without a controlled test."

### 5. Vanity Metrics Deflection

**Rule**: Redirect from metrics that feel good but don't drive decisions.

Vanity metrics to reframe:
- "Total customers" → Reframe as "active customers (purchased in last 90 days)"
- "Total products" → Reframe as "products with sales in the last 30 days"
- "Page views" → Not available via ShopWired API, and not actionable alone anyway
- "Total revenue (all time)" → Reframe as period-specific revenue with trend

### 6. Missing Data Acknowledgement

**Rule**: Always state what you cannot measure. Never let the absence of bad news imply good news.

What ShopWired's API does NOT give you:
- Website traffic or conversion rates
- Marketing channel attribution
- Customer acquisition costs
- Email campaign performance
- Cart abandonment rates
- Product page views or click-through rates
- Profit margins (no cost-of-goods data)
- Shipping costs vs shipping revenue breakdown

When generating reports, include a "Data Limitations" section listing which metrics are unavailable and would require external tools (Google Analytics, email platform, etc.) to measure.

## Report Formatting Standards

### Numbers
- Always convert pence to pounds: `15000` → £150.00
- Use thousands separators: £1,234.56 not £1234.56
- Round percentages to 1 decimal place: 23.4% not 23.3847%
- Show the underlying count alongside every percentage

### Dates
- Use DD/MM/YYYY format (UK standard, as ShopWired is UK-based)
- Always specify the reporting period at the top of every report
- If comparing periods, label both clearly

### Tone
- Be direct, not hedging. But be honest, not promotional.
- "Revenue grew 12%" not "Revenue experienced a positive trajectory"
- "3 products are out of stock" not "There are some inventory considerations"
- Separate facts from recommendations. Present data first, then interpretation, then suggested actions.

### Traffic Light Indicators
Use consistently across all reports:
- 🟢 Healthy / On track / No action needed
- ⚠️ Attention needed / Monitor closely / Mild concern
- 🔴 Urgent / Requires immediate action / Critical issue

## Integration with Other Skills

- **store-intelligence-core**: Required prerequisite. Pence conversion and product hierarchy understanding.
- **inventory-decision-engine**: Feed inventory data into the Inventory Risk Report. Use the Monitor/Alert/Act/Escalate framework for stock-level flags.
- **order-lifecycle-management**: Order status pipeline data for the Store Health Dashboard.
- **customer-segment-intelligence**: Segment distribution for the Customer Health Report. RFM scores for customer metrics.
- **product-catalog-quality**: Quality scores for product performance analysis. Low-quality products with low sales may need content improvement, not discontinuation.
- **pricing-promotion-guard**: When reporting on promotion performance, follow the pricing skill's guardrails. Don't recommend price changes in a report without cross-referencing the safety checks.
- **b2b-wholesale-routing**: If the store has B2B customers, break out B2B vs B2C metrics separately. Blending them produces meaningless averages.
- **multi-channel-sync-governance**: If the store sells on multiple channels, note that ShopWired order data may not capture all sales. Revenue reports from ShopWired alone may undercount total business revenue.

## Common Mistakes to Avoid

1. **Reporting revenue without specifying order statuses**: Always clarify whether "revenue" includes pending orders, completed only, or all non-cancelled orders. The number can differ dramatically.

2. **Averaging averages**: Don't average daily AOVs to get a monthly AOV. Calculate it from totals: total revenue ÷ total orders for the month.

3. **Ignoring the pence trap**: This bears repeating. If you report that "average order value is £12,345" when you meant £123.45, you've lost credibility entirely. Always divide API monetary values by 100.

4. **Year-over-year comparisons with insufficient data**: If the store only has 8 months of data, you cannot do YoY comparisons. Say so rather than fabricating a comparison.

5. **Reporting without actionability**: Every report section should end with "so what?" If a number doesn't lead to a decision, question whether it belongs in the report.

6. **Treating all segments equally in averages**: A store with 10 VIPs (£500 AOV) and 200 one-time buyers (£20 AOV) has a very different profile depending on whether you average or segment. Always break out key metrics by customer segment when available.
