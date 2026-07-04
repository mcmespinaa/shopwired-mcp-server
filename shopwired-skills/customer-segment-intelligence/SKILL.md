---
name: customer-segment-intelligence
description: "Customer classification, segmentation, and lifecycle intelligence for ShopWired stores. Performs RFM analysis (Recency, Frequency, Monetary), detects customer segments (first-time buyers, repeat customers, high-value VIPs, dormant, at-risk churners), and recommends segment-triggered workflows. Integrates with b2b-wholesale-routing for B2B vs B2C classification. Use whenever the user asks about customer segments, customer types, VIP customers, repeat buyers, customer retention, churn risk, customer lifetime value, customer analysis, 'who are my best customers', 'which customers are at risk', customer loyalty, RFM scoring, or customer lifecycle management."
---

# Customer Segment Intelligence

ShopWired's customer data is thin — you get names, emails, company fields, and order history. There are no native tags, no customer groups, no lifecycle stages. This skill turns that sparse data into actionable customer intelligence by deriving segments from purchase behaviour.

The goal is not to build a CRM. It's to answer the questions merchants actually ask: "Who are my best customers?", "Who's about to stop buying?", and "What should I do about it?"

## Prerequisites

Read the store-intelligence-core skill first. Understand prices-in-pence and the product/variation hierarchy before interpreting order values.

## Customer Data Retrieval

ShopWired gives you three tools for customer data:

- `list_customers(count, offset)` — paginated list of all customers
- `get_customer(customer_id)` — full details for one customer
- `get_customer_count()` — total customer count

To get purchase history, you must cross-reference with order tools:

- `search_orders(query=customer_email)` — find orders by customer email
- `get_order(order_id)` — full order details including line items

### Building a Customer Profile

```
1. Call: get_customer(customer_id)
   → Extract: name, email, company, created date

2. Call: search_orders(query=customer_email)
   → Extract: all orders for this customer

3. For each order, call: get_order(order_id)
   → Extract: order date, total value (in pence), status, line items

4. Calculate derived metrics:
   - Total lifetime value = sum of all order totals (convert from pence to £)
   - Order count = number of completed orders
   - Average order value = lifetime value ÷ order count
   - First purchase date = earliest order date
   - Last purchase date = most recent order date
   - Days since last purchase = today - last purchase date
   - Purchase frequency = order count ÷ months since first purchase
```

**Important**: Only count orders with completed/shipped statuses. Exclude cancelled, refunded, and pending orders from lifetime value calculations.

## RFM Scoring Framework

RFM (Recency, Frequency, Monetary) is the standard for behavioural segmentation. Score each dimension 1-5, where 5 is best.

### Recency Score (days since last purchase)

| Days Since Last Purchase | Score | Label |
|---|---|---|
| 0-30 | 5 | Very Recent |
| 31-60 | 4 | Recent |
| 61-120 | 3 | Moderate |
| 121-270 | 2 | Lapsing |
| 271+ | 1 | Dormant |

### Frequency Score (total order count)

| Order Count | Score | Label |
|---|---|---|
| 10+ | 5 | Very Frequent |
| 6-9 | 4 | Frequent |
| 3-5 | 3 | Occasional |
| 2 | 2 | Returning |
| 1 | 1 | One-Time |

### Monetary Score (total lifetime value)

| Lifetime Value (£) | Score | Label |
|---|---|---|
| £1,000+ | 5 | Premium |
| £500-999 | 4 | High |
| £200-499 | 3 | Medium |
| £50-199 | 2 | Low |
| Under £50 | 1 | Minimal |

**Calibration note**: These thresholds suit a mid-range e-commerce store. For luxury goods (average order £500+), shift all monetary thresholds up 5-10x. For low-ticket consumables (average order £10-20), shift them down. Always ask the merchant about their typical order values before presenting RFM results. If you can sample 20-30 orders first, use the median order value to calibrate.

### Combined RFM Score

Total RFM = Recency + Frequency + Monetary (range: 3-15)

## Segment Definitions

Map RFM scores to actionable segments:

### 🌟 VIP Champions (RFM 13-15)
- Recency 4-5, Frequency 4-5, Monetary 4-5
- Your best customers. They buy often, spend a lot, and purchased recently.
- **Action**: Prioritise their experience. Early access to new products, personal thank-you notes, exclusive offers. Never let a VIP support ticket go unresolved.

### 💎 Loyal Regulars (RFM 10-12)
- Recency 3-5, Frequency 3-5, Monetary 3-4
- Consistent buyers with solid lifetime value but not top-tier spenders.
- **Action**: Encourage higher AOV with bundles, upsells, or loyalty rewards. They're already committed — help them spend more per order.

### 🌱 Promising Newcomers (RFM 8-11, Frequency 1-2, Recency 4-5)
- Bought recently, spent decently, but only 1-2 orders.
- **Action**: Critical window. Send post-purchase follow-up within 7 days. Product recommendations based on first purchase. Make the second purchase easy.

### ⚠️ At-Risk (RFM 6-9, Recency 1-2, Frequency 3+)
- Used to buy regularly but haven't purchased in 4-9 months.
- **Action**: Win-back campaign. "We miss you" email with a targeted discount. Check if their last order had any issues (returns, complaints).

### 💤 Dormant (RFM 3-6, Recency 1)
- Haven't purchased in 9+ months. Low engagement across all dimensions.
- **Action**: One final reactivation attempt. If no response, deprioritise but don't delete — they may return during seasonal peaks.

### 🛒 One-and-Done (Frequency 1, Recency 1-2)
- Single purchase, long time ago. Never came back.
- **Action**: Analyse what they bought. If it's a consumable/replenishable product, the repurchase reminder was missed. If it's a one-time purchase category (e.g., furniture), this may be normal.

## Customer Segment Audit

To audit your full customer base:

### Full Audit Sequence

```
1. Call: get_customer_count()
   → Determine total customers and plan pagination

2. Paginate through all customers:
   Call: list_customers(count=50, offset=0)
   Call: list_customers(count=50, offset=50)
   ... continue until all customers retrieved

3. For EACH customer (or a representative sample of 50-100 for large stores):
   a. Call: search_orders(query=customer_email)
   b. For each order: get_order(order_id)
   c. Calculate RFM scores
   d. Assign segment

4. Compile segment distribution
```

**Sampling strategy for large stores (500+ customers)**: Don't process every customer unless asked. Take a stratified sample: the 20 most recent customers, 20 with the most orders, and 20 random customers. This gives a representative view without excessive API calls. Tell the merchant you're working from a sample.

### Audit Output Format

```
## Customer Segment Distribution

Total Customers Analysed: [N]
Analysis Date: [date]
Sample: [Full / Stratified sample of N from M total]

| Segment | Count | % | Avg LTV | Avg Orders | Avg AOV |
|---------|-------|---|---------|------------|---------|
| 🌟 VIP Champions | X | X% | £X | X | £X |
| 💎 Loyal Regulars | X | X% | £X | X | £X |
| 🌱 Promising Newcomers | X | X% | £X | X | £X |
| ⚠️ At-Risk | X | X% | £X | X | £X |
| 💤 Dormant | X | X% | £X | X | £X |
| 🛒 One-and-Done | X | X% | £X | X | £X |

### Health Indicators
- VIP Retention: [VIP count now vs 3 months ago if data available]
- New-to-Repeat Rate: [% of first-time buyers who made a second purchase]
- At-Risk Alert: [number of previously loyal customers now at-risk]
```

## Segment-Triggered Workflows

Each segment maps to specific ShopWired actions:

### VIP Management Workflow
```
When a customer is identified as VIP:
1. Flag for the merchant: "This customer has spent £X across Y orders"
2. Check their most recent order status — ensure it's fulfilled promptly
3. Review their order history for patterns (product preferences, seasonal timing)
4. Suggest: early access to new products, handwritten thank-you with next order
5. If they have a company field → cross-reference with b2b-wholesale-routing
   for potential wholesale pricing
```

### At-Risk Recovery Workflow
```
When a customer is identified as At-Risk:
1. Pull their full order history
2. Check last order for issues:
   - Was it returned or refunded? → Possible quality/fit problem
   - Was there a support complaint? → Check order comments via get_order
   - Was the order delayed? → Possible fulfilment issue
3. Check if products they bought are still active and in stock
4. Recommend: personalised win-back offer via voucher
   - If AOV was £50+: create_voucher with 15% off, min order = their AOV × 0.8
   - If AOV was under £50: create_voucher with flat £5 off, min order = £25
5. Set usage_limit=1, expiry_date=30 days from now
```

### Promising Newcomer Conversion Workflow
```
When a customer is identified as Promising Newcomer:
1. Check what they purchased on their first order
2. Find complementary products in the same category:
   Call: list_products with relevant category filters
3. Check if their purchased product has related items
4. Recommend: follow-up product suggestions, and a "second order" voucher
   - Smaller discount (10%), short expiry (14 days), usage_limit=1
5. Note: if first order was B2B-signalled (high qty, company name),
   route to b2b-wholesale-routing for trade account consideration
```

## Integration with B2B Wholesale Routing

The b2b-wholesale-routing skill classifies customers as B2B vs B2C using signal scoring. This skill extends that with lifecycle intelligence:

- A customer classified as B2B by b2b-wholesale-routing AND scoring as VIP here = **Strategic Account**. Flag for dedicated account management.
- A customer classified as B2B AND scoring as At-Risk = **Revenue Risk**. A lapsing trade account is worth immediate attention.
- A Promising Newcomer with B2B signals = **Trade Prospect**. Fast-track the trade account setup conversation.

When running a segment audit, always note which customers have B2B signals so the merchant can cross-reference.

## Integration with Other Skills

- **store-intelligence-core**: Required prerequisite. Understand pence-to-pounds conversion before calculating monetary scores.
- **b2b-wholesale-routing**: Cross-reference B2B signals with lifecycle segments for account management priorities.
- **order-lifecycle-management**: Check order statuses, returns, and issues when diagnosing At-Risk customers.
- **pricing-promotion-guard**: Use when creating segment-specific vouchers. Follow stacking rules and safety checks.
- **product-catalog-quality**: When recommending follow-up products to Promising Newcomers, check that recommended products score well on quality.
- **reporting-and-insight-framing**: Feed segment distribution data into store-level reports. Avoid misleading metrics (e.g., don't report average LTV across all segments — break it out).

## Common Mistakes to Avoid

1. **Counting cancelled orders in LTV**: Only include completed/shipped orders. A customer with 5 orders and 4 cancellations is not loyal — they're problematic.

2. **Ignoring pence conversion**: An order total of `15000` from the API is £150.00, not £15,000. Get this wrong and your monetary scores are meaningless.

3. **Treating all one-time buyers as failures**: Some products are inherently one-time purchases (mattresses, large appliances). Check the product category before labelling a customer as "One-and-Done" with negative connotations.

4. **Over-segmenting small stores**: A store with 50 customers doesn't need 6 segments. For stores under 100 customers, simplify to 3 groups: Active (ordered in last 90 days), Lapsed (90-270 days), Inactive (270+ days).

5. **RFM without calibration**: The default thresholds won't fit every store. A store selling £5 phone cases has very different monetary scores than a store selling £500 handbags. Always sample actual order data before presenting segments.

6. **Conflating customer count with customer value**: A store might have 2,000 customers but only 50 VIPs generating 60% of revenue. Segment analysis reveals where the real value sits.
