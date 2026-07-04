---
name: onboarding-store-setup
description: "End-to-end onboarding orchestration for new ShopWired stores, from first login to going live. Covers the full 7-phase launch sequence: foundation setup (logo, favicon, contact info, apps), product and catalogue build (categories, brands, products, variations, images), storefront design and branding (theme, colours, banners, navigation), operational configuration (delivery rates, payment gateway, VAT, emails, SEO, analytics, order statuses, invoices, currency), content and legal pages (About Us, Delivery Info, FAQs, Privacy Policy, Refund Policy, T&Cs, Contact Us), pre-launch testing (test purchase, email verification, delivery rate testing, mobile/browser testing, proofreading, 301 redirects), and launch day (DNS, SSL, live payment keys, live test transaction, Google Search Console, announcement). Provides verification checklists at each phase, image specification requirements, admin URL references, and common mistakes to avoid. Use whenever the user asks about setting up a new store, onboarding, store setup, launch checklist, going live, 'I just signed up', 'how do I set up my shop', new store configuration, store launch, getting started, first-time setup, pre-launch, go-live checklist, DNS setup, SSL certificate, payment gateway setup, delivery rate configuration, or any step in the new-store-to-live journey."
---

# Onboarding Store Setup

This skill takes a merchant from "I just signed up" to "my store is live and taking real orders." It's the most sequential skill in the suite — each phase depends on the previous one being complete.

Most new ShopWired merchants don't fail because the platform is hard. They fail because they skip steps, launch too early, or configure things in the wrong order. This skill prevents that by enforcing a structured 7-phase launch sequence with verification gates between phases.

## Prerequisites

Read the store-intelligence-core skill first. The pence-to-pounds conversion, product/variation hierarchy, and API tool mapping all apply throughout onboarding.

## Timeline Overview

| Phase | Name | Typical Timing | Time Required | Owner |
|-------|------|----------------|---------------|-------|
| 1 | Foundation Setup | Week 1 | 2-4 hours | Admin |
| 2 | Product & Catalogue Build | Weeks 1-2 | 4-16 hours | Admin/Team |
| 3 | Storefront Design & Branding | Week 2 | 3-6 hours | Admin/Marketing |
| 4 | Operational Configuration | Weeks 2-3 | 3-5 hours | Admin |
| 5 | Content & Legal Pages | Week 3 | 3-5 hours | Marketing/Legal |
| 6 | Pre-Launch Testing | Weeks 3-4 | 2-4 hours | Admin/Team |
| 7 | Launch Day | Week 4 | 1-2 hours | Admin |

**Total estimated time**: 3-4 weeks, 20-43 hours of active work.

These are estimates. A store with 10 products launches faster than one with 500. Adjust expectations accordingly and tell the merchant upfront.

## Phase 1: Foundation Setup

The admin backbone. Nothing visible to customers yet, but everything else depends on this being right.

### Tasks

#### 1.1 Upload Logo (Required)
- **Admin URL**: `https://admin.myshopwired.uk/business/settings/general`
- **Spec**: Minimum 500px wide, PNG or SVG preferred for transparency
- **What to check**: Logo appears in header, email templates, and invoice PDFs
- **Tip**: A square or landscape orientation works best. Tall/narrow logos cause layout issues in most themes.

#### 1.2 Upload Favicon (Required)
- **Admin URL**: `https://admin.myshopwired.uk/business/settings/general`
- **Spec**: 32×32px, PNG format
- **What to check**: Appears in browser tab when viewing the store
- **Tip**: Use a simplified version of the logo. Detail is lost at 32×32px.

#### 1.3 Set Contact Information (Required)
- **Admin URL**: `https://admin.myshopwired.uk/business/settings/general`
- **Fields**: Business name, email, phone, address
- **What to check**: This information feeds into email templates, invoices, and legal pages. Get it right now.

**Verification via MCP**:
```
Call: get_business_details()
→ Confirm: business name, email, phone, address are all populated
→ Flag any empty fields
```

#### 1.4 Configure Social Media Links (Recommended)
- **Admin URL**: `https://admin.myshopwired.uk/business/settings/general`
- **Fields**: Facebook, Instagram, Twitter/X, Pinterest, TikTok, YouTube
- **Tip**: Only add links to active profiles. Dead social accounts are worse than no social accounts.

#### 1.5 Install Required Apps (Required)

ShopWired has an app ecosystem. These four are near-universal for new stores:

| App | Why | Admin URL |
|-----|-----|-----------|
| **Brands** | Enables brand/manufacturer taxonomy | App Store |
| **User Accounts** | Lets customers create accounts and view order history | App Store |
| **Multi-Currency** | Essential if selling internationally | App Store |
| **Custom Fields** | Adds custom data fields to products and orders | App Store |

**Note**: App installation is not available via the MCP API. Guide the merchant to install these manually through the ShopWired admin. Verify downstream effects (e.g., brands can be managed via MCP after the Brands app is installed).

### Phase 1 Verification Checklist

```
□ Logo uploaded and visible in store header
□ Favicon uploaded and visible in browser tab
□ Business name, email, phone, and address all populated
□ Social media links added (for active profiles only)
□ Brands app installed
□ User Accounts app installed
□ Multi-Currency app installed (if selling internationally)
□ Custom Fields app installed (if needed)
```

**Verification via MCP**:
```
1. Call: get_business_details()
   → Check all contact fields are populated
   → Flag any missing: business name, email, phone, address

2. Call: list_brands()
   → If error or empty: Brands app may not be installed yet
   → If success: app is active

3. Call: list_payment_methods()
   → Store this for Phase 4 reference
```

**Gate**: Do not proceed to Phase 2 until business details are confirmed. Product setup without correct business information means invoices and emails will be wrong.

---

## Phase 2: Product & Catalogue Build

The core of the store. This phase has the widest time range (4-16 hours) because it scales directly with catalogue size.

### Tasks

#### 2.1 Plan Category Hierarchy (Required)
- **Admin URL**: `https://admin.myshopwired.uk/business/products/categories`
- **Before creating anything**: Map out the hierarchy on paper or in a document.
- **Rule**: Maximum 3 levels deep. Deeper hierarchies confuse customers and complicate navigation.
- **Rule**: Keep category names short and descriptive. "Women's Clothing" not "All Types of Clothing for Women and Girls".

**Creating categories via MCP**:
```
1. Create top-level categories first:
   Call: create_category(name="Women's Clothing")
   Call: create_category(name="Men's Clothing")
   Call: create_category(name="Accessories")

2. Then create subcategories with parent_id:
   Call: create_category(name="Dresses", parent_id=[parent_category_id])
   Call: create_category(name="Tops", parent_id=[parent_category_id])

3. Verify structure:
   Call: list_categories()
   → Check hierarchy is correct, no orphaned categories
```

#### 2.2 Create Categories (Required)
- **Admin URL**: `https://admin.myshopwired.uk/business/products/categories`
- Execute the hierarchy planned in 2.1.
- Add category descriptions (helps with SEO).
- Upload category images (900×900px minimum, square format).

#### 2.3 Set Up Custom Fields (Recommended)
- **Admin URL**: `https://admin.myshopwired.uk/business/products/custom-fields`
- Custom fields add structured data to products (e.g., "Material", "Care Instructions", "Country of Origin").
- Plan fields before adding products — retrofitting is tedious.
- **Note**: Custom field management is not available via MCP API. Guide the merchant through admin.

#### 2.4 Create Brands (Recommended)
- **Admin URL**: `https://admin.myshopwired.uk/business/products/brands`
- Only relevant if selling products from named manufacturers/designers.
- Brands enable brand-based navigation and filtering.

**Creating brands via MCP**:
```
Call: create_brand(name="Nike")
Call: create_brand(name="Adidas")

Verify:
Call: list_brands()
→ Confirm all brands created
```

#### 2.5 Add Products (Required)
- **Admin URL**: `https://admin.myshopwired.uk/business/products`
- This is the longest task. For large catalogues, consider batch approaches.

**Creating products via MCP**:
```
Call: create_product(
  title="Classic White T-Shirt",
  price=2999,          ← £29.99 in pence
  description="<p>100% organic cotton classic fit t-shirt.</p>",
  sku="CWT-001",
  stock=50,
  active=true
)
```

**Critical reminders**:
- **Price is in pence**: £29.99 = `2999`. Getting this wrong is the single most common onboarding mistake.
- **Description supports HTML**: Use `<p>`, `<ul>`, `<li>` for structured content.
- **SKU should be unique**: Use a consistent format (e.g., `CATEGORY-NUMBER`).
- **Stock**: Set initial stock levels. If the product has variations, stock is managed at variation level — see 2.6.

#### 2.6 Configure Variations (Required if applicable)
- **Admin URL**: Product edit page → Variations tab
- Variations handle size, colour, material, etc.
- Each variation has independent: price, SKU, stock level, weight.
- **Critical**: Variation-level stock overrides product-level stock. If a product has variations, the product-level stock field is ignored.

**Checking variations via MCP**:
```
Call: list_product_variations(product_id)
→ Verify each variation has: price, SKU, stock level
→ Flag any variations with zero stock or missing SKU
```

#### 2.7 Verify Product Images (Required)
- **Admin URL**: Product edit page → Images tab

**Image Specifications**:

| Image Type | Minimum Size | Format | Notes |
|------------|-------------|--------|-------|
| Product images | 900×900px | JPG/PNG | Square format, white/clean background, 72ppi |
| Category images | 900×900px | JPG/PNG | Consistent style across categories |
| Logo | 500px+ wide | PNG/SVG | Transparent background preferred |
| Favicon | 32×32px | PNG | Simplified logo version |
| Homepage banner (left, Themia theme) | 1000×780px | JPG/PNG | High-impact hero image |
| Homepage banner (right, Themia theme) | 1000×375px | JPG/PNG | Secondary promotional image |

**Checking images via MCP**:
```
For each product:
Call: list_product_images(product_id)
→ Verify at least 1 image exists
→ Flag products with zero images
```

### Phase 2 Verification Checklist

```
□ Category hierarchy created (max 3 levels deep)
□ All categories have descriptions
□ Category images uploaded (900×900px)
□ Brands created (if applicable)
□ All products added with correct prices (in pence!)
□ Product descriptions are complete (not placeholder text)
□ Product images uploaded (900×900px minimum, at least 1 per product)
□ Variations configured with individual prices, SKUs, and stock levels
□ No products with zero stock (unless intentionally out of stock)
□ No products with missing SKUs
```

**Comprehensive verification via MCP**:
```
1. Call: get_product_count() → total products
   Call: get_product_count(active=true) → active products
   → Flag if active < total (some products hidden)

2. Call: list_categories() → verify hierarchy
   → Flag empty categories (categories with no products)

3. Paginate: list_products(count=50, offset=0)
   For each product:
   a. Check price > 0
   b. Check description is not empty
   c. Call: list_product_images(product_id) → verify at least 1 image
   d. If product has variations:
      Call: list_product_variations(product_id)
      → Check each variation has price, SKU, stock
   e. If product has no variations:
      → Check stock > 0 (or confirm intentional OOS)

4. Call: list_brands() → verify brands exist if relevant
```

**Gate**: Do not proceed to Phase 3 until at least your core products are live with images, prices, and stock. A beautiful storefront with no products is pointless.

---

## Phase 3: Storefront Design & Branding

Now you make it look like your store. This is the most subjective phase — merchants can spend days tweaking colours. Set a timebox.

### Tasks

#### 3.1 Select and Apply Theme (Required)
- **Admin URL**: `https://admin.myshopwired.uk/business/design/themes`
- ShopWired offers several themes. Pick one that matches the product type:
  - **Themia**: Good all-rounder, works for most stores
  - Other themes: Browse available options in the admin
- **Tip**: Choose a theme before customising. Switching themes later resets customisations.

#### 3.2 Configure Colours and Fonts (Required)
- **Admin URL**: `https://admin.myshopwired.uk/business/design/theme-editor`
- Match brand guidelines if they exist.
- Key decisions: primary colour, accent colour, background, text colour, heading font, body font.
- **Rule**: Ensure sufficient contrast between text and background. Light grey text on white background is a common accessibility failure.

#### 3.3 Upload Homepage Banners (Required)
- **Admin URL**: `https://admin.myshopwired.uk/business/design/homepage`
- Banner images are the first thing customers see. They set expectations.
- **Themia theme specs**:
  - Left banner: 1000×780px
  - Right banner: 1000×375px
- Include a clear call-to-action on each banner (e.g., "Shop New Arrivals", "Free Delivery Over £50").

#### 3.4 Configure Navigation Menus (Required)
- **Admin URL**: `https://admin.myshopwired.uk/business/design/menus`
- Map navigation to your category hierarchy.
- **Rule**: Maximum 7 top-level menu items. More than 7 overwhelms customers.
- Include: Home, Shop/Categories, About Us, Contact Us as minimum.
- Optional: Blog, Sale, Brands.

#### 3.5 Custom Code Customisations (Optional)
- **Admin URL**: `https://admin.myshopwired.uk/business/design/code-editor`
- For CSS tweaks, custom JavaScript, or theme modifications.
- **Warning**: Only for merchants comfortable with code. Incorrect changes can break the storefront.
- **Tip**: Always note what you changed and keep the original code as a comment. ShopWired doesn't have version control on theme code.

### Phase 3 Verification Checklist

```
□ Theme selected and applied
□ Brand colours and fonts configured
□ Homepage banners uploaded with CTAs
□ Navigation menu configured (max 7 top-level items)
□ Logo displays correctly in chosen theme
□ Store looks acceptable on mobile (preview in admin)
□ Key pages are accessible from navigation (Home, Shop, About, Contact)
```

**Note**: This phase is mostly visual and admin-UI-based. MCP tools don't control theme or design settings. Verification is manual — walk through the store in a browser.

**Gate**: The store should look like a real shop, not a default template. If it still has placeholder banners or lorem ipsum text, it's not ready for Phase 4.

---

## Phase 4: Operational Configuration

The plumbing. None of this is visible to customers, but all of it determines whether orders actually work.

### Tasks

#### 4.1 Set Up Delivery Rates (Required)
- **Admin URL**: `https://admin.myshopwired.uk/business/delivery`
- Configure shipping zones and rates for each delivery method.
- Common setup: UK Standard, UK Express, International Standard.
- Consider free delivery thresholds (e.g., "Free delivery on orders over £50").

**Verification via MCP**:
```
Call: list_shipping_zones()
→ Verify at least one zone exists
→ Check zones cover your target markets

For each zone:
Call: list_shipping_rates(zone_id)
→ Verify rates are set and sensible
→ Flag any zones with zero rates (unless intentionally free)
→ Flag any zones with no rates at all
```

**Common mistakes**:
- Forgetting to set up international shipping (orders from abroad will fail).
- Setting rates too low and absorbing shipping costs unknowingly.
- Not creating a "Rest of World" zone as a catch-all.

#### 4.2 Configure Payment Gateway (Required)
- **Admin URL**: `https://admin.myshopwired.uk/business/payment`
- ShopWired supports: ShopWired Payments (built-in), Stripe, PayPal, and others.
- **Critical**: Use TEST MODE during setup. Do not activate live keys until Phase 7.
- **ShopWired Payments**: Recommended for simplicity. Built-in, no third-party account needed.

**Verification via MCP**:
```
Call: list_payment_methods()
→ Verify at least one payment method is configured
→ Flag if no payment methods found (store cannot accept orders)
```

**Resources**:
- Payment gateway test guide: `https://help.shopwired.co.uk/article/141-how-to-test-your-payment-gateway`
- ShopWired Payments guide: `https://help.shopwired.co.uk/article/356-an-introduction-to-shopwired-payments`

#### 4.3 Configure VAT/Tax Settings (Required for UK)
- **Admin URL**: `https://admin.myshopwired.uk/business/settings/tax`
- UK businesses: Set VAT rate (currently 20% standard rate).
- Decide: Are prices displayed inclusive or exclusive of VAT?
- **B2C default**: Prices include VAT (what customers expect in the UK).
- **B2B consideration**: Some trade stores show prices ex-VAT. Cross-reference with b2b-wholesale-routing skill if the store has B2B customers.

#### 4.4 Customise Email Templates (Required)
- **Admin URL**: `https://admin.myshopwired.uk/business/settings/email-templates`
- ShopWired sends automated emails for: order confirmation, shipping notification, account creation, password reset.
- Customise at minimum: order confirmation and shipping notification.
- Add your logo, brand colours, and contact information.
- **Test**: Send yourself a test email for each template and actually read it.

#### 4.5 Configure SEO Settings (Required)
- **Admin URL**: `https://admin.myshopwired.uk/business/settings/seo`
- Set default meta title format, meta description, and URL structure.
- Enable XML sitemap generation.
- **Tip**: The homepage meta title should be: `Brand Name | What You Sell`. Not just "Home" or "Welcome to My Shop".

#### 4.6 Set Up Analytics (Required)
- **Admin URL**: `https://admin.myshopwired.uk/business/settings/tracking`
- Add Google Analytics tracking code (GA4 measurement ID).
- Add Facebook Pixel if running Facebook/Instagram ads.
- **Do this before launch**: You want analytics tracking from day one. Retroactive data collection is impossible.

#### 4.7 Configure Order Statuses (Recommended)
- **Admin URL**: `https://admin.myshopwired.uk/business/orders/statuses`
- Default statuses: Pending, Processing, Shipped, Completed, Cancelled.
- Add custom statuses if your workflow needs them (e.g., "Awaiting Stock", "Ready for Collection").
- Cross-reference with order-lifecycle-management skill for status transition rules.

#### 4.8 Set Up Invoice/PDF Template (Recommended)
- **Admin URL**: `https://admin.myshopwired.uk/business/settings/invoices`
- Customise the invoice PDF that accompanies orders.
- Include: business name, address, VAT number (if registered), logo, payment terms.
- **Test**: Generate a sample invoice and check formatting.

#### 4.9 Configure Currency Settings (Required if multi-currency)
- **Admin URL**: `https://admin.myshopwired.uk/business/settings/currency`
- Set base currency (typically GBP for UK stores).
- If Multi-Currency app is installed (Phase 1): configure exchange rates and displayed currencies.

**Verification via MCP**:
```
Call: list_countries()
→ Cross-reference with shipping zones — are you shipping to countries
  whose currencies you haven't configured?
```

### Phase 4 Verification Checklist

```
□ Delivery zones and rates configured for target markets
□ Payment gateway configured in TEST mode
□ VAT/tax settings correct (rate, inclusive/exclusive)
□ Email templates customised with logo and brand colours
□ Test emails sent and reviewed for all automated templates
□ SEO settings configured (meta title, description, sitemap)
□ Analytics tracking codes added (Google Analytics, Facebook Pixel)
□ Order statuses configured to match fulfilment workflow
□ Invoice PDF template customised and tested
□ Currency settings correct (base currency, multi-currency if needed)
```

**Gate**: The operational foundation must be solid before adding content pages. A store with beautiful "About Us" content but broken checkout is worse than the reverse.

---

## Phase 5: Content & Legal Pages

The pages customers read before they trust you enough to buy. Legal pages are non-negotiable for UK e-commerce compliance.

### Tasks

#### 5.1 About Us Page (Required)
- **Admin URL**: `https://admin.myshopwired.uk/business/pages`
- Tell your story. Why does this business exist? Who runs it?
- Include: founder story, mission statement, team photo (if appropriate).
- **Tip**: Authenticity sells. Don't write corporate-speak if you're a small business.

#### 5.2 Delivery Information Page (Required)
- **Admin URL**: `https://admin.myshopwired.uk/business/pages`
- Document exactly what you configured in Phase 4.1:
  - Delivery methods and costs
  - Estimated delivery times
  - International shipping availability
  - Free delivery threshold (if applicable)
- **Critical**: This page must match your actual delivery rate configuration. If you offer free delivery over £50 but the page doesn't mention it (or vice versa), customers will lose trust.

#### 5.3 FAQs Page (Recommended)
- **Admin URL**: `https://admin.myshopwired.uk/business/pages`
- Answer the questions you know customers will ask:
  - How do I track my order?
  - What payment methods do you accept?
  - Do you ship internationally?
  - How do I return an item?
  - How long does delivery take?
- Start with 8-10 FAQs. Add more based on actual customer queries post-launch.

#### 5.4 Privacy Policy (Required — legal obligation)
- **Admin URL**: `https://admin.myshopwired.uk/business/pages`
- UK GDPR requires a privacy policy for any site that collects personal data.
- Must cover: what data you collect, why, how it's stored, who it's shared with, customer rights.
- **Warning**: Do not copy a privacy policy from another website. It must be specific to your business.
- **Recommendation**: Use a privacy policy generator or consult a legal professional.

#### 5.5 Refund/Returns Policy (Required — legal obligation)
- **Admin URL**: `https://admin.myshopwired.uk/business/pages`
- UK Consumer Rights Act 2015 gives customers a 14-day right to return online purchases.
- Document: return window, condition requirements, refund method, who pays return postage, process for initiating a return.

#### 5.6 Terms and Conditions (Required — legal obligation)
- **Admin URL**: `https://admin.myshopwired.uk/business/pages`
- Covers: contract formation, pricing accuracy, intellectual property, limitation of liability, governing law.
- **Warning**: T&Cs must be legally sound. Template T&Cs are a starting point but should be reviewed by a solicitor for any serious business.

#### 5.7 Contact Us Page (Required)
- **Admin URL**: `https://admin.myshopwired.uk/business/pages`
- Include: email, phone, business hours, contact form, physical address (if applicable).
- **Tip**: Set response time expectations ("We aim to respond within 24 hours").
- Cross-reference with business details set in Phase 1.3 — they must match.

### Phase 5 Verification Checklist

```
□ About Us page published and accessible from navigation
□ Delivery Information page matches actual delivery rate configuration
□ FAQs page covers common customer questions
□ Privacy Policy page published (GDPR compliant)
□ Refund/Returns Policy published (Consumer Rights Act compliant)
□ Terms and Conditions published
□ Contact Us page published with current contact details
□ All legal pages linked in the website footer
□ Contact details consistent across: business settings, contact page, and invoice template
```

**Gate**: Legal pages must be live before accepting real orders. Operating without a privacy policy or returns policy is a legal risk. Don't skip this phase to "launch faster."

---

## Phase 6: Pre-Launch Testing

The phase most merchants skip. The phase that prevents embarrassing launch-day failures.

### Tasks

#### 6.1 Place a Test Purchase (Required)
- Walk through the complete customer journey:
  1. Browse products
  2. Add to basket
  3. Proceed to checkout
  4. Enter test shipping details
  5. Complete payment (using test gateway credentials)
  6. Confirm order appears in admin
- **Check**: Did the correct delivery rate appear? Was VAT calculated correctly? Did the order total match expectations?

**Verification via MCP**:
```
After placing test order:
Call: list_orders(count=1)
→ Get the test order
Call: get_order(order_id)
→ Verify: line items, prices (in pence ÷ 100 = £), delivery charge, VAT, total
→ Verify: customer details captured correctly
→ Verify: order status is correct (should be pending/processing)
```

#### 6.2 Verify Automated Emails (Required)
- After the test purchase, check:
  - Did the order confirmation email arrive?
  - Does it contain correct: order details, prices, delivery info, branding?
  - Update order status to "Shipped" — did the shipping notification email send?
  - Does it look professional? Is the formatting intact?

#### 6.3 Test Delivery Rate Calculations (Required)
- Place test orders with different scenarios:
  - Minimum order (1 cheap item)
  - Order just below free delivery threshold
  - Order just above free delivery threshold
  - International order (if applicable)
  - Heavy/bulky item (if weight-based shipping)
- **Check**: Do the delivery charges match what you configured?

**Verification via MCP**:
```
Call: list_shipping_zones()
For each zone:
  Call: list_shipping_rates(zone_id)
  → Document the expected rates
  → Compare against actual rates shown during test checkout
```

#### 6.4 Test All Links and Navigation (Required)
- Click every navigation link.
- Click every category link.
- Check that all pages load (no 404 errors).
- Check that all product links work.
- Verify footer links (privacy policy, T&Cs, etc.) all resolve.

#### 6.5 Test Search and Filtering (Required)
- Search for products by name — do they appear?
- Search for products by SKU — do they appear?
- Test category filters — do they show the right products?
- Test sorting (price low-high, price high-low, newest).

**Verification via MCP**:
```
Call: search_products(query="test keyword")
→ Verify relevant products appear
→ Try multiple search terms
```

#### 6.6 Mobile and Browser Testing (Required)
- Test on at minimum:
  - Mobile phone (iPhone and/or Android)
  - Tablet
  - Desktop browser (Chrome, Firefox, Safari)
- Check: layout, readability, image sizing, checkout flow, button sizes.
- **Critical**: Over 60% of e-commerce traffic is mobile. If the mobile experience is broken, you lose the majority of potential customers.

#### 6.7 Proofread All Content (Required)
- Read every page, every product description, every automated email.
- Check for: typos, placeholder text ("Lorem ipsum"), incorrect prices, missing information.
- **Tip**: Get someone who hasn't been involved in setup to proofread. Fresh eyes catch what yours miss.

#### 6.8 Set Up 301 Redirects (Required if migrating)
- **Admin URL**: `https://admin.myshopwired.uk/business/settings/redirects`
- If migrating from another platform, redirect old URLs to new ones.
- This preserves SEO value and prevents customers landing on 404 pages from old bookmarks or search results.
- **Priority**: Redirect your highest-traffic old pages first.

### Phase 6 Verification Checklist

```
□ Test purchase completed successfully
□ Order confirmation email received and reviewed
□ Shipping notification email received and reviewed
□ Delivery rates correct for all scenarios (domestic, international, free threshold)
□ All navigation links working (no 404s)
□ All product links working
□ All footer links working (legal pages)
□ Search returns relevant results
□ Category filtering works correctly
□ Mobile experience tested and acceptable
□ Desktop browser experience tested (Chrome, Firefox, Safari)
□ All content proofread — no typos, no placeholder text
□ 301 redirects configured (if migrating from another platform)
□ Test order cleaned up or marked appropriately in admin
```

**Gate**: Every item on this checklist must pass. One broken checkout link or one incorrect delivery rate will cost you real customers and real money post-launch. Testing is not optional.

---

## Phase 7: Launch Day

Everything before this point has been preparation. This is execution.

### Tasks

#### 7.1 Point DNS to ShopWired (Required)
- Update your domain's DNS records to point to ShopWired's servers.
- **Method**: Add the CNAME or A records provided by ShopWired to your domain registrar.
- **Warning**: DNS propagation takes 1-48 hours. Do this early in the day.
- **Resource**: `https://help.shopwired.co.uk/article/7-pointing-your-domain-to-shopwired`

#### 7.2 Activate SSL Certificate (Required)
- **Admin URL**: `https://admin.myshopwired.uk/business/settings/domains`
- SSL encrypts customer data during checkout. Without it, browsers show "Not Secure" warnings.
- ShopWired provides free SSL. Activate it once DNS is pointing correctly.
- **Wait**: SSL activation may fail if DNS hasn't fully propagated. Retry if needed.
- **Resource**: `https://help.shopwired.co.uk/article/8-setting-up-your-ssl-certificate`

#### 7.3 Switch Payment Gateway to Live Mode (Required)
- **Admin URL**: `https://admin.myshopwired.uk/business/payment`
- Replace test API keys with live API keys from your payment provider.
- **Critical**: Double-check this. Test keys in production = no payments processed. Live keys in test = real charges during testing.
- Verify live credentials are for the correct merchant account.

#### 7.4 Place a Live Test Transaction (Required)
- Make a real purchase with a real payment method.
- Use a small, cheap product or a discounted test product.
- **Verify**:
  - Payment processes correctly
  - Order appears in admin with correct details
  - Confirmation email arrives
  - You can process a refund for the test order
- **Then**: Refund the test transaction.

**Verification via MCP**:
```
After live test transaction:
Call: list_orders(count=1)
Call: get_order(order_id)
→ Verify: payment processed, order details correct
→ Verify: line items, prices, delivery, VAT all correct
```

#### 7.5 Submit to Google Search Console (Required)
- Submit your sitemap URL to Google Search Console.
- Sitemap URL: `https://yourdomain.com/sitemap.xml`
- This tells Google to start indexing your pages.
- **Note**: Indexing takes days to weeks. Submit immediately on launch day.

#### 7.6 Announce Launch (Recommended)
- Post on social media channels configured in Phase 1.4.
- Send an announcement email to your mailing list (if you have one).
- Update your Google Business Profile (if applicable).
- Tell friends, family, and professional network.
- **Tip**: A soft launch (telling a small audience first) lets you catch any remaining issues before a wider announcement.

### Phase 7 Verification Checklist

```
□ DNS pointing to ShopWired (verified via browser)
□ SSL certificate active (padlock icon visible, no "Not Secure" warnings)
□ Payment gateway switched to LIVE mode
□ Live test transaction completed successfully
□ Live test transaction refunded
□ Sitemap submitted to Google Search Console
□ Launch announced on social media / email / network
```

---

## Post-Launch: First 7 Days

The launch is not the end — it's the start. The first week is critical for catching issues.

### Daily checks for the first 7 days:

```
Day 1-3: High vigilance
- Check for new orders every few hours
- Monitor email for customer queries or complaints
- Verify payments are settling in your payment provider dashboard
- Check for any 404 errors in Google Search Console

Day 4-7: Routine monitoring
- Review orders daily
- Check inventory levels (especially fast movers)
- Monitor delivery tracking (are packages arriving?)
- Respond to customer queries within 24 hours
```

**Verification via MCP**:
```
Daily monitoring:
1. Call: list_orders(status="pending")
   → Any orders stuck in pending? Investigate.

2. Call: get_order_count()
   → Track order volume day-over-day

3. Call: list_products(count=50)
   → Spot-check stock levels
   → Flag any products that have gone out of stock

4. Call: get_product_count(active=true)
   → Compare to Phase 2 count — has anything been accidentally deactivated?
```

After the first week, transition to the regular monitoring cadence covered by the reporting-and-insight-framing skill.

---

## Integration with Other Skills

- **store-intelligence-core**: Required prerequisite. Pence-to-pounds conversion applies to every price you set during onboarding. Product/variation hierarchy applies to Phase 2.
- **product-catalog-quality**: After adding products in Phase 2, run a quality audit. Catch missing descriptions, missing images, and incomplete product data before launch.
- **inventory-decision-engine**: After setting initial stock in Phase 2, use this skill to establish reorder points and monitoring thresholds.
- **order-lifecycle-management**: Phase 4.7 order status configuration should align with the status transition rules defined in this skill.
- **pricing-promotion-guard**: If setting up launch promotions or discounts, follow the safety checks in this skill. Don't create a launch voucher that can be stacked with other discounts unintentionally.
- **customer-segment-intelligence**: Not relevant during onboarding (no customers yet), but becomes relevant after the first 30 days of trading.
- **reporting-and-insight-framing**: Transition to this skill after the first-week monitoring period for ongoing store health tracking.
- **b2b-wholesale-routing**: If the store serves both B2B and B2C customers, ensure the onboarding configuration accommodates both (VAT display, customer accounts, pricing structures).
- **multi-channel-sync-governance**: If the store will sell on multiple channels, plan the integration during Phase 4 rather than after launch.

## Common Mistakes to Avoid

1. **Launching without a test purchase**: The single most preventable launch failure. If you didn't test the checkout, you don't know if it works. Test it.

2. **Forgetting to switch from test to live payment keys**: Store launches, customers place orders, payments silently fail. Check Phase 7.3 carefully.

3. **Prices in pounds instead of pence**: Setting a product price to `2999` thinking it's £2,999 when it's actually £29.99, or setting it to `29.99` via the API and getting £0.30. Always remember: the API takes pence.

4. **Skipping legal pages**: Privacy Policy, Returns Policy, and T&Cs are not optional for UK e-commerce. Beyond legal risk, customers check these pages before buying. Missing legal pages = lost trust = lost sales.

5. **Not testing on mobile**: Over 60% of traffic is mobile. A store that looks great on desktop but breaks on mobile loses the majority of potential customers.

6. **Setting up delivery rates after products**: Configure delivery before products. If a customer finds a product before delivery is set up, they can't check out.

7. **DNS changes on a Friday**: DNS propagation can take up to 48 hours and problems are harder to resolve on weekends. Point DNS on a Monday or Tuesday.

8. **No analytics tracking at launch**: Installing Google Analytics a week after launch means you've lost a week of data permanently. Set it up in Phase 4.6 before you go live.

9. **Overcomplicating the category structure**: Three levels deep is the maximum. More than that and customers can't find products, navigation becomes unwieldy, and breadcrumbs break.

10. **Rushing to launch without Phase 6**: Every day of pre-launch testing saves days of post-launch firefighting. The cost of a broken store in production is orders of magnitude higher than the cost of thorough testing.

## Quick Reference: Admin URLs

| Section | URL |
|---------|-----|
| General Settings | `https://admin.myshopwired.uk/business/settings/general` |
| Products | `https://admin.myshopwired.uk/business/products` |
| Categories | `https://admin.myshopwired.uk/business/products/categories` |
| Brands | `https://admin.myshopwired.uk/business/products/brands` |
| Custom Fields | `https://admin.myshopwired.uk/business/products/custom-fields` |
| Themes | `https://admin.myshopwired.uk/business/design/themes` |
| Theme Editor | `https://admin.myshopwired.uk/business/design/theme-editor` |
| Homepage | `https://admin.myshopwired.uk/business/design/homepage` |
| Navigation Menus | `https://admin.myshopwired.uk/business/design/menus` |
| Code Editor | `https://admin.myshopwired.uk/business/design/code-editor` |
| Delivery | `https://admin.myshopwired.uk/business/delivery` |
| Payment | `https://admin.myshopwired.uk/business/payment` |
| Tax/VAT | `https://admin.myshopwired.uk/business/settings/tax` |
| Email Templates | `https://admin.myshopwired.uk/business/settings/email-templates` |
| SEO | `https://admin.myshopwired.uk/business/settings/seo` |
| Tracking/Analytics | `https://admin.myshopwired.uk/business/settings/tracking` |
| Order Statuses | `https://admin.myshopwired.uk/business/orders/statuses` |
| Invoices | `https://admin.myshopwired.uk/business/settings/invoices` |
| Currency | `https://admin.myshopwired.uk/business/settings/currency` |
| Pages | `https://admin.myshopwired.uk/business/pages` |
| Redirects | `https://admin.myshopwired.uk/business/settings/redirects` |
| Domains/SSL | `https://admin.myshopwired.uk/business/settings/domains` |

## Quick Reference: Image Specifications

| Image Type | Minimum Size | Format | Notes |
|------------|-------------|--------|-------|
| Product images | 900×900px | JPG/PNG | Square, clean background, 72ppi |
| Category images | 900×900px | JPG/PNG | Consistent style across categories |
| Homepage banner (left) | 1000×780px | JPG/PNG | Themia theme; hero image with CTA |
| Homepage banner (right) | 1000×375px | JPG/PNG | Themia theme; secondary promo |
| Logo | 500px+ wide | PNG/SVG | Transparent background preferred |
| Favicon | 32×32px | PNG | Simplified logo version |

## Resources

- Store Setup Guide: `https://help.shopwired.co.uk/category/3-store-setup`
- Launch Checklist: `https://help.shopwired.co.uk/article/354-the-shopwired-launch-checklist`
- DNS Setup: `https://help.shopwired.co.uk/article/7-pointing-your-domain-to-shopwired`
- SSL Setup: `https://help.shopwired.co.uk/article/8-setting-up-your-ssl-certificate`
- Delivery Rates: `https://help.shopwired.co.uk/article/15-setting-delivery-rates`
- Payment Gateway Testing: `https://help.shopwired.co.uk/article/141-how-to-test-your-payment-gateway`
- ShopWired Payments: `https://help.shopwired.co.uk/article/356-an-introduction-to-shopwired-payments`
- Bespoke Setup Service: `https://www.shopwired.co.uk/bespoke-setup`
