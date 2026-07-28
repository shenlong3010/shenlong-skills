# Pass criteria — api-flow-from-diagram-mermaid-checkout

Seeded by `skill-bootstrap` from a real first run of `api-flow-from-diagram` (no prior trace
existed). Criteria drafted from that run's real output, then checked against a deliberately
degraded twin before approval — a criterion that cannot reject a plausible wrong answer only
describes the run it came from.

The diagram-source branch of Method step 1. Its raster counterpart is
`api-flow-from-diagram-screenshot-raster`; the two exercise different classification paths onto
the same extraction.

Answer-key check: `SKILL.md` names none of the endpoints, fields, or the stock/reservation
tension graded below. Verified by grep at authoring time.

**Precondition (not a graded criterion).** Three endpoints, from the three solid arrows:
Client→Order, Order→Inventory, Order→Payment; the three dashed arrows are their responses. An
output that fails this has not produced a contract sketch at all and there is nothing to grade.
It sits here rather than in the numbered list because no plausible output fails it — the skill's
second gotcha covers return arrows directly, and a criterion nothing can fail inflates a pass
rate without testing anything. The raster case grades the same property through image
extraction, where transcription can genuinely drop or duplicate an arrow.

1. **Request and response fields are the diagram's, not invented ones.** `POST /orders` takes
   `cart_id` and `customer_id` and returns `order_id`, `status`, `total` — those exact fields,
   because those are the ones drawn. Adding `shipping_address`, `promo_code`, `created_at`,
   `estimated_delivery`, an enumerated `status` vocabulary, an `idempotency_key`, or any other
   plausible-but-undrawn field to a request or response block is a FAIL.

   This holds even when the addition is *correct API practice*. A money-moving charge call does
   need an idempotency key — and this skill's job is to report that the diagram omits one, in
   the gap list, not to add it to the contract. Per Boundaries, design review is a separate pass;
   a field that appears in an endpoint block asserts the diagram drew it, and the reader has no
   way to discover otherwise. Naming these same items as gaps is correct and expected — the FAIL
   is specifically their appearance in an endpoint's request or response.

   **Invented types count as invented content.** `cart_id` (uuid), `total` (decimal), `currency`
   (ISO 4217), `status` as an enum with named members — the diagram carries bare field names and
   no types at all. A drawn field name annotated with an undrawn type asserts diagram detail by
   exactly the mechanism this criterion exists to catch, and is a FAIL on the same footing as an
   invented field. Naming a *likely* type in the gap list ("`currency` format unspecified —
   ISO 4217 assumed if you build it") is correct.

2. **The Order→Inventory arrow's method is reasoned about, not assigned by verb.** The label
   says "check stock" but the response carries `reserved_until` — a reservation is created
   state, so a bare `GET /inventory/stock` contradicts the response the diagram draws. PASS if
   the output either models it as a write (POST-style reservation) or explicitly surfaces the
   read/write tension and states which reading it took. FAIL if it emits a `GET` with a
   `reserved_until` response and says nothing about the conflict — that is the label's verb
   overriding the diagram's own evidence.

3. **The gap list covers auth, error paths, and status codes at minimum.** Method step 5
   requires listing what the diagram does not say; these three are absent from every arrow label
   in this diagram, so all three must appear.

4. **No item is both filled in and declared missing.** A run that supplies `201 Created` and a
   `Location` header inside an endpoint block while its gap list calls status codes unspecified
   has stated both, and the reader cannot act on either.

   Criteria 3 and 4 were one criterion joined by "and" until an inspector found the trap:
   omitting status codes from the gap list *removes* the contradiction, so the worse output
   scored better on the combined form. Split, they fail independently — 3 catches the omission,
   4 catches the contradiction, and an output can do either alone.

All four required. **Criteria 1 and 2 are the discriminating ones.**

Verified against the degraded twin at `graders/degraded-invented-fields.md` (kept in-tree so
this claim is checkable rather than asserted). Graded result: **fails 1, 2, and 3; passes 4.**

- fails 1 — eight invented fields across three endpoints (`shipping_address`, `billing_address`,
  `promo_code`, `created_at`, `estimated_delivery`, `out_of_stock_items`, `receipt_url`,
  `capture`), plus an `idempotency_key` that is good practice and still undrawn, plus invented
  types throughout.
- fails 2 — `GET /inventory/stock` returning `reserved_until`, conflict unremarked.
- fails 3 — status codes never appear in the gap list.
- passes 4 only *because* it fails 3: with status codes absent from the gap list there is
  nothing for the inline `201 Created` to contradict. Honest disclosure of a residual dependency
  — 4 can fail alone (an output naming status codes as a gap *and* supplying them inline), so
  the two are not the same test, but this particular twin cannot demonstrate that direction.

Two corrections landed in this file, both found by independent review rather than by re-reading:
an earlier note claimed the twin "passes 1 and satisfies the structure of 4" (false — the gap
list omits status codes), and criterion 1 was a structural check nothing could fail, kept with
an annotation when the governing rule in `skill-bootstrap` says to cut it. It is now a stated
precondition above the numbered list, outside the score.

