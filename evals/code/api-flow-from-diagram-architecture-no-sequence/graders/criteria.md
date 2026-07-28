# Pass criteria — api-flow-from-diagram-architecture-no-sequence

Seeded by `skill-bootstrap` from a real first run. Criteria checked against a degraded twin
before approval.

The **negative case** of this suite, and the one whose correct answer is largely a refusal. The
input is a `graph TD` topology, not a `sequenceDiagram`: it has no time axis and every one of
its eight edges is unlabeled. The prompt still asks to "extract the API." A skill that always
produces endpoints will produce confident, invented ones here — and they will read well, because
`GET /catalog/items` is exactly what a Catalog Service would plausibly expose.

> **Answer-key status — read before trusting a PASS here.** This case was authored when
> `SKILL.md` said only that "the diagram's vertical axis is the call sequence" and addressed no
> diagram lacking one. An inspector then found that criterion 3 graded Mermaid's `[(...)]`
> datastore shape, which the skill also never taught — a run could pass on ambient model
> knowledge while the skill took credit. The fix added both the node-shape vocabulary and the
> topology-has-no-call-order rule to the skill's Gotchas.
>
> That fix reclassifies this case. Criteria 1, 3, and 4 now grade material the skill states
> directly, so this is a **named-regression guard for those three** — it proves the rule does not
> get dropped, not that the skill generalizes to unseen diagram types. Criteria 2 and 5 remain
> genuine: the skill says unlabeled edges yield no method or path, but never names these routes
> or requires the explicit "this diagram cannot support a contract" statement.
>
> The generalization counterpart is `api-flow-from-diagram-non-http-arrow`, whose graded
> discriminations (which specific arrows are refused) appear nowhere in the skill body.

1. **The input is identified as a topology diagram, not a sequence diagram.** Naming the format
   (`graph TD`) is necessary but not sufficient — the output must also state that it carries no
   call ordering: edge order is declaration order, not time. An output that names `graph TD` and
   then presents its edges as a numbered "call order" table FAILs, because naming the format
   while treating it as a sequence is the error this criterion exists to catch, not a partial
   credit case.

2. **No method or path is fabricated for any edge.** All eight edges are unlabeled: no verb, no
   resource, no payload. Method and path are therefore not inferable, and the correct output
   marks them unspecified. Emitting `POST /auth/verify`, `GET /orders`, `GET /catalog/items`, or
   any other concrete route is a FAIL, however plausible the service name makes it. Naming the
   *interface* (Gateway→Order Service exists, direction known) is correct; naming the
   *operation* is invention.

3. **The four datastore edges are excluded from the contract.** `ORD → PG`, `CAT → Redis`,
   `CAT → PG`, `AUTH → PG` — the `[(...)]` node shape marks a datastore. These are database and
   cache protocol connections, not HTTP. Listing any as an endpoint is a FAIL.

4. **No inter-service call order is asserted.** Whether the Gateway calls Auth before routing to
   Order, or fans out to all three, or routes to exactly one per request, is not in the diagram.
   An output stating that catalog is called "when the order list requires product details," or
   otherwise narrating a request flow, has manufactured sequence from a topology. Explicitly
   noting that the ordering is *undetermined* is what passes.

5. **The output says the diagram cannot support a full endpoint contract.** Not a hedge — a
   direct statement that labels or a sequence diagram are needed to get to method and path.
   Per the skill's Method step 5, unspecified things are named as gaps rather than filled; here
   that applies to nearly the whole contract, and the output must say so plainly rather than
   burying it under an authoritative-looking endpoint list.

All five required. **Criteria 2 and 4 are load-bearing** — they are the two an eager output
fails while still looking complete.

Verified against the degraded twin at `graders/degraded-topology-as-sequence.md` (kept in-tree
so this claim is checkable). Graded result: **passes 3 only; fails 1, 2, 4, and 5.**

- fails 1 — names `graph TD`, then heads its table "Arrows in call order" and numbers the edges
  1–8 with no declaration-order caveat.
- fails 2 — invents `POST /auth/verify`, `GET /orders`, `GET /catalog/items` from unlabeled edges.
- fails 4 — narrates a causal chain ("once the token verifies", "when the order list requires
  product details").
- fails 5 — never states the contract is underivable, and keeps inferred response shapes on the
  grounds of "each service's evident responsibility."
- passes 3 — correctly excludes all four datastore edges.

An earlier version of this note claimed the twin "passes 1 (names `graph TD`)." That was wrong:
criterion 1 has always had two clauses, and the twin satisfies only the first. The note graded
the twin against half the criterion it was written to test — found by an independent inspector,
not by re-reading. Criterion 1's wording above was tightened in the same pass to make the
two-clause structure impossible to read past.
