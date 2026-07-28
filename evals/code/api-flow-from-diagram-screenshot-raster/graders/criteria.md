# Pass criteria — api-flow-from-diagram-screenshot-raster

Seeded by `skill-bootstrap` from a real first run. Criteria checked against a degraded twin
before approval.

The **raster branch** of Method step 1 — the diagram arrives as a PNG, so the run must route
through `read-image` before extracting. Its text-source counterpart is
`api-flow-from-diagram-mermaid-checkout`. Neither case covers the other: a skill could parse
Mermaid perfectly and never handle an image, which is the common real-world input.

Fixture: `fixtures/profile-flow.png` — a rendered sequence diagram, "user-profile flow · v2",
four participants, eight arrows.

Answer-key check: `SKILL.md` names `read-image` as the raster route but names no participant,
endpoint, or field graded below. Verified by grep at authoring time.

1. **The image is actually read, and all eight arrows are recovered.** Four participants (Mobile
   App, Auth Service, Profile Service, Photo Store) and eight arrows in vertical order. A run
   that describes the image only in general terms, or that recovers fewer than eight arrows
   without saying which were illegible, FAILs — transcription fidelity is the whole risk of the
   raster branch, and a silently dropped arrow is a silently dropped endpoint.

2. **Exactly four calls appear in the contract sketch — no return arrow becomes an endpoint.**
   Four solid arrows carry calls; four dashed arrows carry their responses. A fifth entry in the
   sketch, or any endpoint whose request fields are a dashed arrow's payload (`access_token` /
   `expires_in`, `avatar_url`, `updated_at`), is a FAIL per the skill's second gotcha.

   This fails independently of 1 and 4: an output can recover all eight arrows with correct
   styles (passing 1), transcribe the three labeled endpoints exactly (passing 4), and still
   emit a spurious fifth block for the `access_token` return. The property is what reaches the
   sketch, not what was read — which is why it grades the sketch's contents rather than the
   arrow table's style column.

   **Scope: request fields only.** A dashed arrow's payload appearing as an endpoint's
   *response* is correct and expected — that is what a response is. `avatar_url` is arrow 5's
   payload and belongs in arrow 4's response block. Only a dashed payload showing up as a
   *request* (or as a block of its own) indicates a return arrow was mistaken for a call. Do not
   broaden this to "any fields" — that would fail the degraded twin on two criteria instead of
   one and destroy its single-property isolation.

3. **The Photo Store arrow is not turned into a REST endpoint.** Its label is `fetch avatar
   blob` — no method, no path, and "Photo Store" reads as object storage rather than a REST
   service. Emitting `GET /photos/{user_id}/avatar` or any similar invented route is a FAIL.
   PASS if the output either marks the transport unspecified or names it as a probable blob-store
   access, and says the diagram does not state it. This is the raster twin of the checkout case's
   invented-field criterion: the surrounding arrows *do* carry real methods and paths, which is
   exactly what makes filling this one in feel consistent rather than fabricated.

4. **The three labeled endpoints keep their drawn methods and paths.** `POST /login`,
   `GET /profile/{user_id}`, `PATCH /profile/{user_id}` — the image states these explicitly, so
   a mismatch is a transcription error, not a judgment call. Their fields must also match:
   login takes `email`/`password` and returns `access_token`/`expires_in`; the PATCH takes `bio`
   and returns `updated_at`.

5. **The specific auth-propagation gap is named, not just "auth."** The skill's Method step 5
   lists auth first, so any run reaching that step mentions it — a generic mention proves
   nothing. What this criterion requires is the observation the diagram actually supports:
   `access_token` is returned by `POST /login` and **no arrow shows it travelling to Profile
   Service**, so the propagation mechanism is unstated. A gap list saying only "auth is not
   specified" FAILs; one naming the returned-but-never-sent token passes.

All five required. **Criterion 3 is load-bearing**; 1 and 4 guard the transcription that the
raster branch exists to test.

Verified against the degraded twin at `graders/degraded-blobstore-as-rest.md` (kept in-tree so
this claim is checkable). Graded result: **passes 1, 2, 4, and 5; fails only 3** — a faithful
transcription with a correct gap list that nonetheless emits `GET /photos/{user_id}/avatar` with
a path parameter and a `none` request body, as if the route were drawn. Single-property failure
is deliberate: it isolates criterion 3 from the transcription criteria, so a FAIL here cannot be
explained by sloppy reading.

Criterion 2 was originally worded as "solid and dashed arrows are distinguished," which a
reviewer flagged as overlapping 1 and 4 — an output distinguishing styles in its arrow table
almost necessarily recovered the arrows and assigned the fields correctly. It now grades the
contract sketch's contents instead of the arrow table's annotations, which is the property the
skill's second gotcha actually protects and which fails on its own.
