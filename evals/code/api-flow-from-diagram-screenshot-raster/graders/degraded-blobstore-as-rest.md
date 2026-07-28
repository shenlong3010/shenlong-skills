## Extraction (via read-image)

**Type:** rendered sequence diagram, "user-profile flow · v2".

**Participants:** Mobile App, Auth Service, Profile Service, Photo Store.

| # | Source → Target | Label | Style |
|---|---|---|---|
| 1 | Mobile App → Auth Service | `POST /login  (email, password)` | solid |
| 2 | Auth Service → Mobile App | `access_token, expires_in` | dashed |
| 3 | Mobile App → Profile Service | `GET /profile/{user_id}` | solid |
| 4 | Profile Service → Photo Store | `fetch avatar blob` | solid |
| 5 | Photo Store → Profile Service | `avatar_url` | dashed |
| 6 | Profile Service → Mobile App | `display_name, bio, avatar_url` | dashed |
| 7 | Mobile App → Profile Service | `PATCH /profile/{user_id}  (bio)` | solid |
| 8 | Profile Service → Mobile App | `updated_at` | dashed |

---

## API contract sketch

### 1. `POST /login`
- **Caller → callee:** Mobile App → Auth Service
- **Request:** `email`, `password`
- **Response:** `access_token`, `expires_in`
- **Triggered by:** user submits credentials at the start of the flow.

### 2. `GET /profile/{user_id}`
- **Caller → callee:** Mobile App → Profile Service
- **Path params:** `user_id`
- **Response:** `display_name`, `bio`, `avatar_url`
- **Triggered by:** successful login.

### 3. `GET /photos/{user_id}/avatar`
- **Caller → callee:** Profile Service → Photo Store
- **Path params:** `user_id`
- **Request body:** none
- **Response:** `avatar_url`
- **Triggered by:** step 2, server-side, while assembling the profile response.

### 4. `PATCH /profile/{user_id}`
- **Caller → callee:** Mobile App → Profile Service
- **Path params:** `user_id`
- **Request:** `bio`
- **Response:** `updated_at`
- **Triggered by:** user edits their profile after the read.

---

## What the diagram does not say

- **Auth propagation.** `access_token` is returned by login but no arrow shows it travelling to Profile Service; the header and scheme are unstated.
- **Status codes.** None for any of the four calls.
- **Error responses.** No failure paths — bad credentials, unknown user, Photo Store unavailable.
- **Content types.** JSON assumed but never stated.
- **Field formats.** `expires_in` units and `updated_at` format are unspecified.
- **Concurrency.** No ETag or version field on the PATCH.
