# Pass criteria — api-flow-from-diagram-non-http-arrow

Seeded by `skill-bootstrap` from a real first run. Criteria checked against a degraded twin
before approval.

This case grades the skill's **first gotcha**: a diagram arrow is not always an HTTP call. The
flow deliberately mixes one real endpoint with a SQL write, a Kafka publish, a Kafka consume,
and a self-call. A skill that maps arrows to endpoints mechanically produces four or five
endpoints here and looks thorough doing it.

Answer-key check: `SKILL.md`'s gotcha names "message queues, database reads, and internal
function calls" as a category but names no topic, table, or endpoint graded below. The category
is stated in the skill; the discrimination is not.

1. **`POST /orders` is present and correctly shaped.** From the Client→Order arrow: request
   `cart_id`, response `order_id` and `status`. Path equivalents are fine; the graded property
   is that the one real endpoint is transcribed accurately.

   Scope note: this criterion grades **that endpoint's shape only**, not how many endpoints the
   output emits. The count belongs to criterion 2 — an earlier wording ("exactly one HTTP
   endpoint") put the count here too, so any output inventing a broker route failed 1 and 2
   together and the pair became one test scored twice.

2. **The DB, Kafka, and self-call arrows are explicitly refused as endpoints.** Each of
   `O->>DB` (SQL insert), `O->>K` (publish), `K->>N` (consume), and `N->>N` (internal render)
   must be identified as a non-HTTP interaction. Presenting any of them as a route — including
   plausible-looking internal ones like `POST /internal/orders/persist`,
   `POST /events/order.created`, or `POST /notifications/order-created` — is a FAIL. This is the
   criterion the case exists for: the participant type and label are the evidence, and a route
   invented over a datastore or broker edge is a contract the reader would try to build.

   Scope note: this criterion grades **misclassification only**. An arrow the output never
   mentions at all is criterion 3's failure, not this one — silence is not a wrong
   classification. Read the FAIL rule above ("presenting any of them as a route") as operative;
   an arrow that is absent cannot have been presented as anything.

3. **Every arrow is accounted for somewhere in the output.** An output that lists only
   `POST /orders` and never mentions the other four arrows has skipped Method step 2 rather than
   completed it — the reader cannot tell whether they were considered and rejected or simply
   missed. Each of the five arrows must appear.

   Scope note: this criterion grades **presence only**. Whether an arrow is correctly classified
   as a non-endpoint is criterion 2's job. Keeping them separate is deliberate — an output can
   mention every arrow and misclassify three (fails 2, passes 3), or classify correctly but
   silently drop two (passes 2, fails 3). An earlier wording folded "marked as a non-endpoint"
   into this criterion, which made it un-failable independently of 2: any output failing 2 also
   failed 3, so the pair was one test scored twice.

4. **Gaps are named.** Auth, status codes, and error responses at minimum. The `order.created`
   event schema is the substantive one here — it crosses a service boundary and the diagram
   never states its fields — but naming it is not required to pass; the general gap list is.

All four required. **Criterion 2 is load-bearing**; 3 catches the opposite failure, an output
too sparse to audit.

**Two degraded twins**, because one could not separate criteria 2 and 3. Both in-tree so these
claims are checkable rather than asserted.

`graders/degraded-broker-as-endpoint.md` — **passes 1, 3, and 4; fails 2.** It promotes the DB
insert, the Kafka publish, and the Kafka consume into three named routes
(`POST /internal/orders/persist`, `POST /events/order.created`,
`POST /notifications/order-created`), refusing only the self-call. It passes 1 because its
`POST /orders` block is itself correctly shaped, and 3 because every arrow does appear — wrongly
classified, but present. Both of those passes depend on the scope notes in criteria 1 and 3: an
earlier draft folded the endpoint count into 1 and the classification into 3, which made this
twin fail three criteria for one underlying error.

`graders/degraded-silent-omission.md` — **passes 1, 2, and 4; fails 3.** It emits exactly one
endpoint, correctly, and simply never mentions the DB, Kafka, or self-call arrows. Nothing is
misclassified, so criterion 2 has nothing to catch; the reader still cannot tell whether four
arrows were considered and rejected or never read. This twin exists solely to give criterion 3
an independent failure.

Note on how this got here: criterion 3 originally read "must appear somewhere in the output,
marked as such" — two clauses, and every output failing the second also failed criterion 2,
making 3 un-failable on its own. The accompanying note also claimed the broker twin passed 3
while grading only the first clause. Both were found by an independent reviewer. The criterion
is now presence-only and the second twin gives it teeth.

**Generalization status.** The skill's first gotcha names the category ("message queues,
database reads, and internal function calls"), and a later edit added a specific clause: *"A
self-arrow (`N->>N`) is an internal call, never an endpoint."* `N` is this fixture's own
participant alias, so the `N->>N` portion of criterion 2 is a **named-regression guard** — the
skill states that exact verdict, in that exact notation.

The DB, Kafka publish, and Kafka consume discriminations remain genuine generalization: no
Kafka, no `order.created`, no `INSERT INTO`, no Orders DB, and no participant graded for them
appears in the skill body. One qualification on an earlier blanket grep claim — the string
`/orders` *does* appear at `SKILL.md:20`, as `GET /orders/{id}` in an illustrative sentence about
path formatting. It is not a verdict about this flow and does not seed any graded
discrimination, but "no route appears in the skill body" was too absolute as written.

Read a PASS accordingly: three of the four refusals are evidence the category rule fires on
unseen material; the fourth is evidence it did not regress.
