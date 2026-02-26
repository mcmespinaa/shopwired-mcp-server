# ShopWired MCP Server — Bug Fixes

## What Changed

After testing against the live ShopWired API, we found that several field names and parameters didn't match the actual API responses. Here's a summary:

### 1. Product Names Showing as "Unknown"
- **Cause:** We used `product.get("name")` but ShopWired returns `title`
- **Fix:** Changed to `product.get("title")` in formatting.py

### 2. Search Returning 400 Error
- **Cause:** We sent search as a query parameter to `/products` — but ShopWired has a separate endpoint
- **Fix:** Changed to `GET /products/search?query=...`

### 3. Prices Showing £0.00
- **Cause:** ShopWired stores prices in **pence** (e.g., 9000 = £90.00), and we displayed the raw value
- **Fix:** Added `format_price()` function that converts pence to pounds

### 4. Status Showing as "N/A"
- **Cause:** We looked for `status` (string) but ShopWired uses `active` (boolean/0-1)
- **Fix:** Changed to read `active` field, displays "Active" or "Hidden"

### 5. Pagination Not Working
- **Cause:** We used `page` parameter but ShopWired uses `offset` (number of items to skip)
- **Fix:** Changed all pagination from `page` to `offset`, `limit` to `count`

## How to Apply

Copy each file to its corresponding location in your project:

```
shopwired-fixes/utils/formatting.py  →  src/shopwired_mcp/utils/formatting.py
shopwired-fixes/tools/products.py    →  src/shopwired_mcp/tools/products.py
shopwired-fixes/tools/orders.py      →  src/shopwired_mcp/tools/orders.py
shopwired-fixes/tools/customers.py   →  src/shopwired_mcp/tools/customers.py
shopwired-fixes/tools/store.py       →  src/shopwired_mcp/tools/store.py
```

From your project root:
```bash
cd /Users/UPCHANNEL/Documents/GitHub/shopwired-mcp-server/shopwired-mcp-server

cp <downloads>/shopwired-fixes/utils/formatting.py src/shopwired_mcp/utils/formatting.py
cp <downloads>/shopwired-fixes/tools/products.py src/shopwired_mcp/tools/products.py
cp <downloads>/shopwired-fixes/tools/orders.py src/shopwired_mcp/tools/orders.py
cp <downloads>/shopwired-fixes/tools/customers.py src/shopwired_mcp/tools/customers.py
cp <downloads>/shopwired-fixes/tools/store.py src/shopwired_mcp/tools/store.py
```

Then restart Claude Desktop to reload the MCP server.
