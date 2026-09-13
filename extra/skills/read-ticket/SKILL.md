---
name: read-ticket
description: Extract an actionable spec from a messy issue tracker item — Jira, GitHub/GitLab issue, Linear, or a pasted bug report — separating the real ask from the noise, surfacing hidden acceptance criteria, and naming unstated dependencies before any code is planned. Use whenever a ticket, issue, or bug report is the input to work — "what is this ticket actually asking", "turn this issue into tasks", "is this ready to build", "what's the acceptance here", or before /decompose or plan-writer runs on issue text. Do NOT use for a clean, already-decomposed task file (that is decompose's input) or for reading a spec PDF/contract (that is read-pdf-doc).
derivation: original
flow: lookup
domain: process
---

# Read Ticket

Turn a human-written tracker item into a spec an executing agent can act on — the real ask, the acceptance, and the gaps — before a plan is built on top of it.

## Scope boundary

This reads *unstructured intent*: what a human filed, in whatever shape they filed it. It is the step *before* `decompose` (which needs a clean goal) and before `plan-writer`. A ticket that is already a crisp, verifiable task does not need this skill. Reading a formal spec document (PDF contract, RFC, OpenAPI file) routes to `read-pdf-doc` / `read-api-spec`, not here.

## Output: the ticket brief

Whatever the source format, produce the same brief before answering or handing off:

- **Real ask** — one sentence, in the filer's intended outcome terms, not their proposed solution. Filers often describe a fix ("add a retry"); the ask is the underlying need ("requests fail intermittently"). State the need; note the proposed solution separately as *one* candidate.
- **Type** — bug / feature / chore / question / spike. A "bug" with no reproduction is really a question; label it so.
- **Acceptance criteria** — what observably makes this done. Most tickets state none. Derive the *implied* acceptance and mark each as `stated` or `inferred` — inferred criteria are questions for the filer, not commitments.
- **Unstated dependencies** — systems, data, access, migrations, or upstream tickets this silently assumes exist. These are the run-killers.
- **Scope edges** — what is explicitly out, and what is ambiguously in (the "and while you're there…" trap).
- **Blocking unknowns** — the questions that must be answered before estimation is honest. If any exist, the ticket is *not* ready to build; say so plainly.

Answer the user's actual question from this brief; emit the full brief when they ask "is this ready" or "turn this into tasks".

## Reading procedure

1. **Separate report from diagnosis from proposal.** A ticket often braids three things: what the user saw (symptom), why the filer thinks it happens (guess — treat as unverified), and what they want done (proposal). Split them. The filer's diagnosis is a hypothesis, not a finding.
2. **Find the real ask under the proposed solution.** Ask "if this exact proposal were impossible, what would still need to be true?" That is the ask.
3. **Harvest acceptance from anywhere it hides** — the title, a comment thread, a linked design doc, an attached screenshot, a "definition of done" checklist. Comments frequently override the original description; the newest authoritative comment wins.
4. **Name what's assumed.** Every external system, credential, feature flag, dataset, or sibling ticket named or implied → list it as a dependency to confirm exists.
5. **Rate readiness**, one of: `ready` (ask + acceptance + deps all clear), `needs-answers` (list the blocking unknowns), `needs-split` (multiple independent asks braided into one ticket — enumerate them).

## Gotchas

- **The title lies or under-describes.** Titles are written first, before the filer understood the problem; the real ask is usually three comments deep. Never brief from the title alone.
- **Comments supersede the description.** A six-month-old description with a recent "actually we decided to…" comment means the comment is the spec. Read chronologically; let the latest authoritative voice win, and flag the contradiction rather than silently picking one.
- **"Simple" and "just" are scope traps.** "Just add a button" tickets routinely hide auth, state, and persistence work. Rate readiness on the implied work, not the filer's adjective.
- **A bug with no reproduction is not a bug yet.** No steps-to-reproduce + no expected-vs-actual = a question. Don't let it enter a build loop as if it were specified — the first task would be "reproduce", which `systematic-debug` owns.
- **Linked ≠ read.** A ticket that says "see linked doc for details" has no acceptance *in the ticket*. Either the link is fetched and its acceptance pulled forward, or the ticket is `needs-answers`. Do not assume the link says what you'd hope.
- **Multiple asks in one ticket.** "Fix the export and also speed up the dashboard" is two tickets. Mark `needs-split` and enumerate — never plan a compound ticket as one unit; the acceptance can't be single-valued.

## Boundaries

- Once the brief is `ready`, hand the real-ask + acceptance to `decompose` (task units) or `plan-writer` (execution plan) — this skill produces the input those consume, it does not itself decompose.
- A bug ticket that reaches `ready` and needs reproduction routes to `systematic-debug`; a pasted stack trace inside the ticket routes to `stacktrace-analyzer`.
- Fetching a linked GitHub/Jira item's content, when a tracker MCP or `web-research` is available, is a fetch step — do it, then read the fetched text here. This skill reasons over text; it does not itself call the tracker API.
