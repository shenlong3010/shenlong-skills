---
name: read-api-spec
description: Comprehend an API contract — OpenAPI/Swagger (JSON or YAML), GraphQL SDL, Postman collection, or gRPC/proto — into what endpoints exist, what shapes they take, how auth works, and where the traps are, so you can call it or build against it correctly. Use whenever an API definition is the input — "what does this API do", "how do I call this endpoint", "what auth does this need", "is this request shaped right", "diff these two API versions", or before writing a client against a spec file. Do NOT use for a live API with no spec (probe it with http-requests) or for mechanically querying the spec's JSON (that is data-query).
derivation: original
flow: lookup
domain: code
---

# Read API Spec

Turn an API contract into the facts you need to call it or build against it: the endpoints, the shapes, the auth, and the failure modes — without reading the whole document into context.

## Scope boundary

This reads a *contract that exists as a file or document*: OpenAPI/Swagger, GraphQL SDL, Postman collection, proto. A live endpoint with no published spec is probed, not read — route to `http-requests` (make a call, observe the shape). Mechanically extracting one field from a large spec JSON (`paths./users.get.responses`) is a `data-query` jq job, not a comprehension task; use this skill when the question is "what can this API do / how do I use it", not "what's the value at this path".

## Output: the API brief

- **Surface** — the endpoints/operations that matter to the task, each as `METHOD path` (REST) or `Query/Mutation name` (GraphQL), with a one-line purpose. For a large spec, brief only the operations the task needs — never enumerate all 200.
- **Shapes** — request body / params and response body for those operations, to the field level that matters: required vs optional, types, enums, and any field whose name lies about its type (a `count` that's a string, an `id` that's a UUID vs int).
- **Auth** — the scheme (apiKey / bearer / OAuth2 / mTLS), *where* the credential goes (header name, query param, cookie), and which operations require which scopes. This is the field most specs bury and clients get wrong.
- **Errors & status** — the documented non-2xx responses and what they mean; note operations that document *only* the happy path (an undocumented-error trap).
- **Versioning & base** — server base URLs, version in path vs header, and deprecation markers.

Answer the user's actual question from this brief; emit the full brief only for "help me build a client" scale requests.

## Reading procedure

1. **Parse, don't grep.** OpenAPI/GraphQL are structured — load them as data (`data-query` for a big JSON/YAML spec) and navigate `paths`/`components` or the SDL type graph. Grepping a minified single-line swagger.json is a false-positive machine.
2. **Follow `$ref` to ground truth.** OpenAPI schemas are a reference graph; a request body is usually `$ref: '#/components/schemas/Foo'`. Resolve the ref before describing the shape — the inline description is a pointer, not the shape.
3. **Read auth from `securitySchemes` + `security`.** The scheme is defined once in `components.securitySchemes`; each operation's `security` block (or the global default) says which applies. GraphQL hides auth in directives or out-of-band docs — say so if it's not in the SDL.
4. **Locate the base URL(s)** from `servers` (OpenAPI) — there are often multiple (prod/staging); pick deliberately, don't assume the first.
5. **Flag the gaps.** No documented error responses, `additionalProperties: true` (undocumented fields allowed), `nullable` fields, `oneOf`/`anyOf` polymorphism the client must discriminate — call these out; they're where integrations break.

## Gotchas

- **`required` is per-object, not global.** In OpenAPI a field's `required` lives on the parent schema's `required:` array, not on the property. A property can look optional in its own definition and be required by its parent. Check the array.
- **`$ref` cycles and depth.** Schemas reference each other, sometimes circularly. Resolve to the depth the task needs, note recursion rather than expanding it infinitely.
- **Swagger 2.0 ≠ OpenAPI 3.x.** 2.0 uses `definitions` + `parameters` with `in: body`; 3.x uses `components.schemas` + `requestBody`. Auth blocks differ too. Check the `swagger:`/`openapi:` version field first — describing 2.0 with 3.x vocabulary misleads.
- **GraphQL has no endpoints.** One URL, POST, operation selected by query body. "Which endpoint" is the wrong question; the surface is the root `Query`/`Mutation`/`Subscription` fields. Describe those, and note that field selection determines response shape.
- **The example is not the schema.** `example:` values are illustrative and frequently stale or invalid against their own schema. Describe from the schema; treat examples as hints only.
- **Auth-in-URL is a leak.** If the spec puts an API key in a query param, note it — those land in access logs and referrer headers. Route the security concern to `security-review` if building against it.

## Boundaries

- Writing the actual client call routes to `http-requests` (sessions, retries, auth headers) — this skill tells you *what* to send; that skill sends it robustly.
- A live API with no spec is probed, not read — `http-requests` to observe real responses.
- Deep field-path extraction from the spec file is `data-query` (jq/yq); this skill is comprehension, not extraction.
- Security concerns about the API you're consuming (auth-in-URL, missing authz on an operation) route to `security-review`.
