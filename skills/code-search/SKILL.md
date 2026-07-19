---
name: code-search
description: Find code and context efficiently — the lexical → structural → semantic search ladder with token-budget discipline, plus the first-contact orientation pass for an unfamiliar repo. Use whenever locating code — "where is X defined", "who calls Y", "find the config for Z", tracing dependencies, any moment a plain grep is about to be fired at a repo — and on first contact with a codebase: "how does this codebase work", "where do I start", "map this repo". Covers ripgrep/ugrep flags that cut both wall time and output tokens, and when to escalate to ast-grep.
derivation: original
flow: lookup
domain: code
---

# Code Search

Three layers; start at the cheapest, escalate only when the layer below can't express the query. The cost that matters twice: wall time AND output tokens — search results are uncurated payload straight into context.

## The ladder

**1. Lexical (default): ripgrep-class.** Exact strings and regex, gitignore-aware, parallel. This resolves the overwhelming majority of "where is / who uses" queries. Note the surface: recent Claude Code native builds run ugrep under Bash instead of the old rg-based Grep tool (Copilot CLI/Codex still ship rg) — the flags below are grep-compatible where it matters; verify the binary with `command -v rg ugrep`.

**2. Structural: ast-grep (`sg`).** When the query is about code *shape*, not text: "calls to `foo` with exactly two args", "try blocks with empty catch", "this function renamed but not its overloads". Metavariables express what regex can't:

```bash
sg run -p 'foo($A, $B)' -l python          # calls with exactly two args
sg run -p 'try { $$$ } catch ($E) { }' -l ts   # empty catch blocks
```

Regex matching code structure is a false-positive machine (comments, strings, formatting variants); AST patterns aren't.

**3. Semantic (last resort): embeddings / repo-map tools.** Only when neither the symbol name nor an exact string is known ("where does authorization happen conceptually"). Benchmarks (CoREB, 2026) show short keyword queries — the form agent searches actually take — collapse semantic retrieval to near-useless; a symbol name you half-remember is better spent on layer 1 with fuzzy help (`ugrep -Z`) than on an embedding index.

## Lexical efficiency patterns (time + tokens)

```bash
rg -l 'PaymentRouter'            # files-only FIRST, then targeted read — the core loop
rg -F 'a.b[0]->c'                # -F literal: no regex engine, no escaping bugs
rg -w 'id'                       # word boundaries — 'id' not 'identifier'
rg -t java 'SnsPublisher'        # type scoping; -g 'src/**' for globs
rg -n 'retry' src/ | head -50    # cap high-frequency queries — the dominant token saver
rg -c 'TODO'                     # counts, not contents, when counts answer the question
rg --max-columns 200 'minified'  # don't let one minified line eat the window
rg -uu 'needle'                  # escape hatch when gitignore/hidden hides the target
rg -z 'error' logs/*.gz          # search inside compressed files
git grep --cached 'flag'         # tracked-content-only, index-fast
fd 'Publisher'                   # FILENAME search — stop grepping for filenames
```

- Add `-C n` context only when actually needed — context lines inflate output 2–6× depending on match density; default to bare matches, then read the file at the hit.
- **Budget rule:** search output ≤ ~15% of the context window; hitting it means stop searching and proceed with what you have (context-economy rule, applied).

## First contact with an unfamiliar repo

Orientation before search — five probes, one screen of output, time-boxed (this is orientation, not an audit):

1. **Identity:** README first 50 lines + manifest (pom/build.gradle/package.json/pyproject/go.mod) → language, framework, the dependencies that define the architecture (web framework, queue client, ORM).
2. **Commands:** real build/run/test invocations from manifest scripts, Makefile/justfile, or CI config — CI is the ground truth for "how it actually builds".
3. **Layout:** top 2 directory levels; role of each top dir in ≤ 6 words; flag generated/vendored dirs to ignore.
4. **Entry points:** main()/handler/server bootstrap; route registration; scheduled jobs and consumers.
5. **Hot paths:** the 3–5 files most central to change — churn (`git log --stat` heuristics), most-imported modules, core domain types.

Read files, don't guess from names — a `utils/` dir can hide the core. Output: identity line, commands block, annotated tree, entry points, hot-path list with one-line reasons.

## Performance honesty

Speed claims are pattern-dependent: literal-rich patterns are where rg-class tools are 5–13× grep; literal-poor patterns (`[A-Za-z]{30}`) hit a cliff on every tool, and high match counts flatten all differences (output handling dominates). rg-vs-ugrep is contested and configuration-sensitive (ugrep needs gitignore explicitly enabled). Never claim "X is faster" without the pattern class; benchmark on your corpus when it matters.

## Boundaries

- Symbol definitions, references, call hierarchies → `symbol-lookup` (ctags/ast-grep rungs, LSP ceiling stated); grep finds text, not scope-resolved symbols.
- Monorepo/org scale (millions of files, cross-repo) → indexed servers (zoekt-class); out of this skill's scope.
- Filename lookups → `file-find`; git history → `git-search`; structured data (JSON/YAML) → `data-query`; runtime who/what → `system-lookup`; diagram/text-format files → `read-diagram`; log dumps → `log-triage`; web content → `web-research`.
