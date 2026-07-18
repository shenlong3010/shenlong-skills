---
name: log-triage
description: Triage a raw log dump into clustered errors, a timeline, and the anomaly that matters. Use when logs are pasted or fetched — "what's wrong in these logs", "triage this", incident-time log reading — use INSTEAD of reading a raw dump top-to-bottom.
derivation: original
flow: debug
domain: system
---

# Log Triage

## Method
1. **Normalize:** strip volatile tokens (timestamps→bucket, ids/uuids/ips→placeholders) so identical failures cluster instead of appearing unique.
2. **Cluster:** group by normalized message + source; report count, first-seen, last-seen per cluster. Volume ≠ importance — a single new FATAL outranks 10k known WARNs.
3. **Timeline:** order cluster first-occurrences; mark the phase shift (the minute the error mix changed) — that is usually the incident start, and what changed then (deploy, config, traffic) is the lead.
4. **Correlate:** request/trace ids that appear across clusters tie symptoms to one cause; follow one exemplar id end-to-end rather than reading breadth-first.
5. **Output:** cluster table (count, span, one exemplar line), the phase-shift timestamp, top hypothesis + the log query that would confirm it.

## Rules
Quote exemplar lines exactly — paraphrased errors can't be grepped. Say explicitly when the dump's time window is too narrow to contain the cause.
