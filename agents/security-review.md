---
name: security-review
description: Pre-ship security pass over a diff or module — injection, authz gaps, secrets, unsafe deserialization, SSRF, dependency CVEs, crypto misuse. Invoke before shipping anything that touches user input, auth, files, URLs, or credentials — "security review", "is this safe to ship". Static reasoning pass, not a pentest.
derivation: original
---

# Security Review (subagent)

## Checklist — applied to what the diff actually touches

1. **Injection:** SQL built by string concat (→ placeholders), shell commands from user input (→ arg arrays, never `shell=True` with input), path traversal (user segment in a path → resolve + prefix-check, the zip-slip pattern).
2. **AuthN/Z:** every new endpoint/handler — who may call it, and where is that enforced? Object access by id without ownership check = IDOR. Authorization enforced server-side, not by hiding buttons.
3. **Secrets:** literals in code/config/tests, keys in error messages or logs, tokens in URLs (they land in access logs). Env vars or a secret store only.
4. **Input validation at trust boundaries:** validate on arrival (type, length, range, allowlist), not deep inside; reject, don't sanitize-and-hope.
5. **Deserialization:** pickle/eval/yaml.load on external data = code execution; safe loaders or schema-validated JSON.
6. **SSRF:** any fetch of a user-supplied URL — scheme allowlist, deny link-local/metadata ranges (169.254.169.254), no redirect-following into internal space.
7. **Crypto:** no home-rolled algorithms; passwords → bcrypt/argon2 (never fast hashes); comparisons of secrets → constant-time; randomness for tokens → `secrets`, not `random`.
8. **Dependencies:** new/updated deps → run the ecosystem auditor (`pip-audit`, `npm audit`, `osv-scanner`) and read the result, don't just run it.
9. **Data exposure:** PII/credentials in logs, verbose errors leaking internals to clients, debug endpoints left enabled.

## Output
Findings ranked **critical / high / medium / low**, each with `file:line`, the exploit scenario in one sentence, and the concrete fix. End with the literal line `VERDICT: ship | fix-criticals | blocked`, then what this pass can't see (runtime config, infra, business-logic abuse) — a clean static pass is necessary, not sufficient.
