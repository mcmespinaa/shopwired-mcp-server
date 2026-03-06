# API Permissions Reference

Each tool maps to one ShopWired REST API call. This document lists the HTTP method and endpoint for each tool so you can configure API key permissions accordingly.

## Products (read/write)

| Tool | Method | Endpoint | Type |
|------|--------|----------|------|
| search_products | GET | /products/search | Read |
| get_product | GET | /products/{id} | Read |
| list_products | GET | /products | Read |
| get_product_count | GET | /products/count | Read |
| list_product_variations | GET | /products/{id}/variations | Read |
| list_product_images | GET | /products/{id}/images | Read |
| create_product | POST | /products | Write |
| update_product | PUT | /products/{id} | Write |
| update_stock | PUT | /products/{id} or /products/{id}/variations/{vid} | Write |
| delete_product | DELETE | /products/{id} | Delete |

## Orders (read/write)

| Tool | Method | Endpoint | Type |
|------|--------|----------|------|
| list_orders | GET | /orders | Read |
| get_order | GET | /orders/{id} | Read |
| search_orders | GET | /orders/search | Read |
| get_order_count | GET | /orders/count | Read |
| update_order_status | POST | /orders/{id}/status | Write |
| add_order_comment | POST | /orders/{id}/comments | Write |
| delete_order | DELETE | /orders/{id} | Delete |

## Customers (read/write)

| Tool | Method | Endpoint | Type |
|------|--------|----------|------|
| list_customers | GET | /customers | Read |
| get_customer | GET | /customers/{id} | Read |
| get_customer_count | GET | /customers/count | Read |
| create_customer | POST | /customers | Write |

## Store Configuration

| Tool | Method | Endpoint | Type |
|------|--------|----------|------|
| list_categories | GET | /categories | Read |
| create_category | POST | /categories | Write |
| update_category | PUT | /categories/{id} | Write |
| delete_category | DELETE | /categories/{id} | Delete |
| list_brands | GET | /brands | Read |
| create_brand | POST | /brands | Write |
| list_vouchers | GET | /vouchers | Read |
| create_voucher | POST | /vouchers | Write |
| delete_voucher | DELETE | /vouchers/{id} | Delete |
| list_gift_cards | GET | /gift-cards | Read |
| list_shipping_zones | GET | /shipping-zones | Read |
| list_shipping_rates | GET | /shipping-zones/{id}/rates | Read |
| list_webhooks | GET | /webhooks | Read |
| create_webhook | POST | /webhooks | Write |
| get_business_details | GET | /business-details | Read |
| list_countries | GET | /countries | Read |
| list_payment_methods | GET | /payment-methods | Read |
