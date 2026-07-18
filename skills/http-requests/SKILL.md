---
name: http-requests
description: Call HTTP APIs robustly with requests — sessions, retries with backoff, timeouts, streaming, auth, corporate-proxy TLS. Use whenever scripting API calls, webhooks, downloads, or any HTTP integration — "call this API", "download this file", "hit this endpoint from Python".
derivation: original
flow: util
domain: web
---

# http-requests

```bash
pip install requests
```

## The one rule
**requests has NO default timeout** — a hung server hangs your script forever. Every call gets `timeout=(connect, read)`:

```python
r = requests.get(url, timeout=(3.05, 30))
r.raise_for_status()          # or you'll parse an error page as data
data = r.json()
```

## Session + retries (the production shape)

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

s = requests.Session()
s.headers.update({"Authorization": f"Bearer {token}", "User-Agent": "my-tool/1.0"})
retry = Retry(total=4, backoff_factor=0.5,
              status_forcelist=(429, 500, 502, 503, 504),
              allowed_methods=("GET", "PUT", "DELETE"))   # POST only if idempotent
s.mount("https://", HTTPAdapter(max_retries=retry))
```

Session = connection pooling + shared headers; without it, every call pays a new TLS handshake.

## Gotchas
- `json=payload` sets the header and serializes; `data=payload` form-encodes — mixing them up produces 400s that look like auth errors.
- **Large downloads:** `stream=True` + `iter_content(chunk_size=1 << 20)`; without stream, the whole body lands in memory.
- **Corporate TLS interception:** `SSLError: self-signed certificate in chain` behind a proxy → point at the corp CA bundle via `REQUESTS_CA_BUNDLE=/path/ca.pem` (env) — never `verify=False` in anything committed.
- 429 handling: honor `Retry-After` (Retry does, respect it in manual loops too).
- `r.json()` on empty/HTML body raises — check `r.headers.get("content-type")` when APIs misbehave.
