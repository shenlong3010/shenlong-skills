---
name: concept-explain
description: Build a working mental model of a technical concept that has no single source document — what problem it exists to solve, the model itself, a worked example, where the intuition breaks, and what it gets confused with — then check the model landed. Use whenever the ask is understanding a concept rather than reading an artifact — "explain consistent hashing", "how does OAuth actually work", "I don't understand CRDTs", "what is a bloom filter", "why do we need X", "explain like I'm a backend dev", "I keep confusing X and Y", "make this click". Do NOT use when a specific artifact is in hand — a paper (paper-notes / paper-deep-dive), a blog post (read-eng-blog), a talk (talk-notes), or code in this repo (explain-code / trace-flow).
derivation: original
flow: lookup
domain: docs
---

# Concept Explain

Every other reader in this toolbox starts from an artifact — a URL, a file, a paper, a function. This skill starts from a *gap*: a concept the user cannot yet reason with, where no single document is the answer and the work is constructing a model rather than extracting one.

## Scope boundary

If an artifact is in hand, this is the wrong skill — route by artifact type (see Boundaries). This skill owns the case where the user names a concept, not a source. It also owns the case where an artifact was read and the concept *still* didn't land: the reader skills report what a source said, this one builds the model the source assumed you already had.

## Output: the concept brief

Order is load-bearing — motivation before mechanism, always.

- **The problem** — what breaks without this concept. Concrete and specific: a scenario where the naive approach fails. A concept explained before its problem is memorized, not understood.
- **The model** — the core idea in plain terms, one paragraph. The thing you'd sketch on a whiteboard. Prefer one precise analogy over three loose ones, and state where the analogy stops holding.
- **Worked example** — one small concrete instance, walked end to end with real values. Not a definition restated; an actual trace. This is where understanding usually happens.
- **Where the intuition breaks** — the case the tidy model gets wrong. Every simplification has an edge it mispredicts; naming it is what separates a model you can *use* from one you can only recite.
- **Confusables** — the neighbors this gets mixed up with, and the one distinguishing question that separates them. Include only real confusions, not a taxonomy tour.
- **Where it shows up** — where the user would actually meet this: a system, a protocol, a library, a failure mode in their own stack.

Then, and only then, the check.

## The comprehension check

Close with **one** question the user answers — not a quiz, a probe that fails loudly if the model didn't land. Good probes require *applying* the model, not restating it:

- A small variation of the worked example ("what happens if the third node leaves instead?")
- A "would this work" scenario that's wrong for a reason the brief covered
- A "which of these two would you reach for, and why"

One question. Not three. The point is a single load-bearing check the user can decline, not homework. If they answer and the model is off, correct the specific misconception rather than re-explaining from the top — a repeat of the same explanation fails the same way twice.

## Procedure

1. **Establish the starting point before explaining.** What the user already knows determines where the explanation begins — the same concept needs a different bridge for someone who knows hash tables than for someone who doesn't. Infer from context (their stack, the repo, what they've asked before) and state the assumption in one clause: "assuming you're comfortable with X". If the gap is too wide to guess, ask one question — never a questionnaire.
2. **Find the problem first.** Before writing the model, name what fails without it. If you can't state the failure concretely, the explanation will be a definition, not an understanding.
3. **Build the model, then attack it.** Draft the plain-terms model, then find its edge — the case where it mispredicts. That edge goes in the brief. A model with no stated limit is a model the user will over-apply.
4. **Make the example real.** Concrete values, actual steps. "Suppose we hash keys A, B, C onto a 0–255 ring" beats "keys are distributed across the ring."
5. **Verify current facts, don't recite them.** Anything version-specific, protocol-specific, or subject to change (default parameters, algorithm choices, current best practice) gets checked against a source via `web-research` — not answered from memory. The model is durable; the specifics rot.
6. **Ask the one check question.**

## Gotchas

- **Explanation before motivation is memorization.** The mechanism-first ordering feels efficient and produces recall without understanding: the user can repeat the definition and cannot apply it. Always lead with what breaks.
- **Analogies leak, and unmarked leaks become the misconception.** "A bloom filter is like a guest list" holds until someone asks about removals — and if the boundary was never stated, the analogy *becomes* the user's model and they now confidently believe wrong things. State the limit in the same breath as the analogy.
- **The correct-and-useless explanation.** Precise, complete, technically unimpeachable, and it doesn't land. This is the default failure of explaining from a definition outward. The test isn't "is this accurate" — accuracy is table stakes — it's "could they now predict what happens in a case I didn't cover."
- **A concept the user half-knows is harder than one they don't.** Existing wrong models actively resist correction; new information gets absorbed *into* the misconception rather than replacing it. When their question reveals a broken model, name and dismantle it explicitly ("the thing that's off is X") before building — additive explanation on top of a wrong foundation doesn't take.
- **Don't teach the taxonomy.** Listing every variant and adjacent concept feels thorough and dilutes the one model that needed to land. Confusables earn their place only when the user is plausibly conflating them right now.
- **Memory is stale for anything versioned.** Concepts are stable; their instantiations aren't — default algorithms change, protocols deprecate, "current best practice" moves. Route version-specific claims through `web-research` rather than confident recall, and say which parts are timeless model versus checked specifics.
- **The check question is not a quiz.** A question answerable by restating the brief verifies nothing — the user pattern-matches text they just read. Require application: a variation, a prediction, a choice between options.

## Boundaries

- An artifact in hand routes by type — research paper: `paper-notes` (verdict) or `paper-deep-dive` (full read); engineering blog or architecture post: `read-eng-blog`; conference talk or video: `talk-notes`; PDF report or spec: `read-pdf-doc`; API contract: `read-api-spec`.
- A concept *in this codebase* — "what does this function do", "how does our auth work" — is `explain-code` (one unit) or `trace-flow` (one path across files). This skill is for concepts that exist independently of any repo.
- Needing to find sources before explaining is `web-research`; chain it in, don't reimplement fetching here.
- Practicing *articulating* a concept under interview conditions is `interview-drill` — that drills recall and delivery, this builds the model in the first place.
- If understanding the concept was the prelude to a design decision, the decision itself is `adr-lite` (record it) or `brainstorm` (shape it).
