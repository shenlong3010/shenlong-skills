**Input classification:** Mermaid `graph TD` source, parsed directly as diagram source text.

## Participants and arrows

**Participants:** Load Balancer, API Gateway, Auth Service, Order Service, Catalog Service, Redis, Postgres.

**Arrows in call order:**

| # | Source → Target | Kind |
|---|---|---|
| 1 | LB → GW | forward |
| 2 | GW → AUTH | HTTP |
| 3 | GW → ORD | HTTP |
| 4 | GW → CAT | HTTP |
| 5 | ORD → PG | database |
| 6 | CAT → CACHE | cache |
| 7 | CAT → PG | database |
| 8 | AUTH → PG | database |

## Contract sketch

### 1. `POST /auth/verify`
- **Caller → callee:** API Gateway → Auth Service
- **Request:** bearer token from the inbound request
- **Response:** `user_id`, `scopes`, `valid` (boolean)
- **Triggered by:** every request arriving from the Load Balancer, before routing.

### 2. `GET /orders`
- **Caller → callee:** API Gateway → Order Service
- **Request:** `user_id` from the verified token
- **Response:** list of orders
- **Triggered by:** step 1, once the token verifies successfully.

### 3. `GET /catalog/items`
- **Caller → callee:** API Gateway → Catalog Service
- **Request:** query filters
- **Response:** list of catalog items
- **Triggered by:** step 2, when the order list requires product details for rendering.

**Not endpoints — datastore edges:** `ORD → PG`, `CAT → Redis`, `CAT → PG`, `AUTH → PG` are database and cache protocol connections, not HTTP calls.

## What the diagram does not say

- **Auth scheme details.** An Auth Service exists but the token format and header are unstated.
- **Status codes.** None drawn.
- **Error responses.** No failure paths.
- **Pagination.** The catalog and order list endpoints would need it; not shown.
- **Content types.** JSON assumed.
- **Response shapes.** `graph TD` has no return arrows, so response fields above are inferred from each service's evident responsibility.
