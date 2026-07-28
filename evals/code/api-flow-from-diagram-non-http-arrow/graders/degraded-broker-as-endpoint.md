**Input:** Mermaid `sequenceDiagram` source, parsed directly.

**Participants:** Client, Order Service, Orders DB, Kafka, Notification Service.

**Arrows in order:**
1. `C->>O` submit order (cart_id)
2. `O->>DB` INSERT INTO orders
3. `DB-->>O` order_id
4. `O->>K` publish order.created
5. `K->>N` consume order.created
6. `N->>N` render email template
7. `O-->>C` order_id, status

---

## Contract sketch

### 1. `POST /orders`
- **Caller → callee:** Client → Order Service
- **Request:** `cart_id` (string)
- **Response:** `order_id` (string), `status` (string)
- **Triggered by:** client submission; entry point.

### 2. `POST /internal/orders/persist`
- **Caller → callee:** Order Service → Orders DB
- **Request:** the order row fields implied by the cart
- **Response:** `order_id`
- **Triggered by:** step 1, immediately after validation.
- The diagram shows `INSERT INTO orders` with a return value, so this is modelled as a persistence endpoint returning the generated identifier.

### 3. `POST /events/order.created`
- **Caller → callee:** Order Service → Kafka
- **Request:** `order_id`, event metadata
- **Response:** none drawn (fire-and-forget)
- **Triggered by:** step 3, after the order id is available.

### 4. `POST /notifications/order-created`
- **Caller → callee:** Kafka → Notification Service
- **Request:** the `order.created` payload
- **Response:** none drawn
- **Triggered by:** step 4; delivery of the published event.

**Internal (not an endpoint):** `N->>N` render email template — a self-call within the Notification Service, no interface crossed.

---

## What the diagram does not say

- **Auth.** Nothing on any hop, internal or external.
- **Status codes.** None given for any of the four endpoints.
- **Error responses.** No failure path drawn for persistence, publish, or delivery.
- **Event schema.** `order.created` fields beyond `order_id` are unspecified.
- **Content types.** JSON assumed throughout.
- **Idempotency.** No key on `POST /orders` despite retry risk.
- **Delivery semantics.** At-least-once vs exactly-once is unstated, so dedupe requirements on the Notification Service are undetermined.
