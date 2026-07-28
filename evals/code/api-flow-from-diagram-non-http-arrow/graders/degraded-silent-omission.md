**Input:** Mermaid `sequenceDiagram` source, parsed directly.

**Participants:** Client, Order Service, Orders DB, Kafka, Notification Service.

## Contract sketch

### `POST /orders`
- **Caller → callee:** Client → Order Service
- **Request:** `cart_id` (string)
- **Response:** `order_id` (string), `status` (string)
- **Triggered by:** client submission; entry point of the flow.

This is the only HTTP endpoint in the diagram.

## What the diagram does not say

- **Auth.** No scheme on the client-facing call.
- **Status codes.** None given.
- **Error responses.** No failure path for an invalid or already-submitted `cart_id`.
- **Content types.** JSON assumed, never stated.
- **Idempotency.** No key on `POST /orders` despite the retry risk on a submit.
- **`status` values.** Returned but never enumerated.
