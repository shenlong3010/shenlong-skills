## Input classification

Mermaid `sequenceDiagram` source text — parsed directly.

## Participants and arrows

**Participants:** Client, Order Service, Payment Service, Inventory Service.

| # | Type | Source → Target | Label |
|---|---|---|---|
| 1 | solid | Client → Order Service | create order (cart_id, customer_id) |
| 2 | solid | Order Service → Inventory Service | check stock for cart items |
| 3 | dashed | Inventory Service → Order Service | available: true, reserved_until |
| 4 | solid | Order Service → Payment Service | charge (amount, currency, payment_method_id) |
| 5 | dashed | Payment Service → Order Service | payment_id, status |
| 6 | dashed | Order Service → Client | order_id, status, total |

## Contract sketch

### 1. `POST /orders`
- **Caller → callee:** Client → Order Service
- **Request:** `cart_id` (uuid), `customer_id` (uuid), `shipping_address` (object), `billing_address` (object), `promo_code` (string, optional)
- **Response:** `order_id` (uuid), `status` (enum: `pending` | `confirmed` | `failed`), `total` (decimal), `created_at` (ISO 8601), `estimated_delivery` (ISO 8601)
- **Status:** `201 Created`, `Location: /orders/{order_id}`
- **Triggered by:** client checkout submission.

### 2. `GET /inventory/stock?cart_id={cart_id}`
- **Caller → callee:** Order Service → Inventory Service
- **Request:** `cart_id` as query parameter
- **Response:** `available` (boolean), `reserved_until` (ISO 8601), `out_of_stock_items` (array)
- **Status:** `200 OK`
- **Triggered by:** step 1.

### 3. `POST /payments/charges`
- **Caller → callee:** Order Service → Payment Service
- **Request:** `amount` (decimal), `currency` (ISO 4217), `payment_method_id` (string), `idempotency_key` (uuid), `capture` (boolean, default true)
- **Response:** `payment_id` (string), `status` (enum: `succeeded` | `pending` | `declined`), `receipt_url` (string)
- **Status:** `201 Created`
- **Triggered by:** step 3, on `available: true`.

## What the diagram does not say

- **Auth.** No scheme shown on any hop.
- **Error paths.** Only happy paths are drawn.
- **Content types.** JSON assumed.
- **Retry semantics.** Not indicated for the Payment hop.
