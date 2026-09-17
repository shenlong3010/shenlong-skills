#!/usr/bin/env bash
# UserPromptSubmit: when a prompt is a short bare imperative ("add caching to
# the API"), append a note naming the fields it left unstated, so the model
# asks instead of guessing. Aimed at one-shot success rate: the measured
# failure mode is a terse work request with no success criteria, where the
# model picks an interpretation and builds the wrong thing.
#
# Field vocabulary from ai_workflow.pdf's template (ROLE/TASK/CONTEXT/INPUTS/
# CONSTRAINTS/EXAMPLES/REASONING/OUTPUT/SUCCESS). Only SUCCESS and CONSTRAINTS
# are named here -- they're the two a hook can honestly judge from prompt text
# alone. CONTEXT/INPUTS live in upstream artifacts (BRIEF.md, plan.md) this
# hook cannot see, so it does not claim to check them.
#
# Emits PLAIN TEXT on stdout, not JSON: docs confirm UserPromptSubmit adds
# plain stdout to context on exit 0. Deliberate -- the cavemem hook in this
# same event array emits its own JSON, and two JSON emitters on one event
# risk a parse collision. Plain text sidesteps that entirely.
#
# NO rate limiting yet, on purpose. Whether this becomes noise is an empirical
# question -- ~/.claude/nudge.log records every fire so the real rate can be
# measured before inventing a suppression rule for a problem that may not exist.
payload=$(cat)
PY=python3; [ "$(python3 -c 'print(1)' 2>/dev/null)" = "1" ] || PY=python

result=$(printf '%s' "$payload" | PYTHONIOENCODING=utf-8 "$PY" -c "
import json, sys, re

try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)

text = (d.get('user_input') or '').strip()
if not text:
    sys.exit(0)

words = text.split()
# Long prompts already carry their own context; only terse ones are at risk.
if len(words) > 15:
    sys.exit(0)

# Bare imperative = starts with an action verb. A question ('why does X') or a
# statement is not a work request and gets no nudge.
VERBS = {
    'add','fix','make','build','create','refactor','update','change','write',
    'implement','remove','delete','rename','move','convert','migrate','set',
    'wire','hook','port','split','merge','extract','optimize','clean','handle',
}
if words[0].lower().strip('.,:;!?') not in VERBS:
    sys.exit(0)

low = text.lower()
missing = []
# SUCCESS: any done-condition language at all.
if not re.search(r'\b(so that|until|should|must|pass(es|ing)?|works?|verif|test|expect|accept|criteri|done when)\b', low):
    missing.append('SUCCESS (how to tell it worked)')
# CONSTRAINTS: any stated boundary, exclusion, or non-negotiable.
if not re.search(r\"\b(don't|do not|without|only|must not|never|keep|preserve|avoid|no |instead of|except)\b\", low):
    missing.append('CONSTRAINTS (what not to touch or change)')

# Fire only when BOTH are absent -- the genuinely bare request. A prompt that
# states success criteria OR constraints is already half-framed, and nudging it
# is closer to nagging than helping. Narrow on purpose: the point is that when
# this does fire, it's worth reading.
if len(missing) < 2:
    sys.exit(0)

print('NUDGE:' + ' and '.join(missing))
" 2>/dev/null | tr -d '\r')

[ -z "$result" ] && exit 0

missing_fields=${result#NUDGE:}
ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "$ts missing=$missing_fields" >> "$HOME/.claude/nudge.log"

echo "[prompt-framing] This request omits $missing_fields. Ask for the missing piece before implementing, or state the assumption you're making explicitly so it can be corrected."
exit 0
