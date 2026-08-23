#!/usr/bin/env python3
"""Eval Lint — structural validation of golden cases under evals/.

Checks, per case directory (evals/<domain>/<case-id>/):
  - prompt.md exists and is non-empty
  - graders/criteria.md exists and is non-empty
  - fixture paths referenced as `fixtures/...` in prompt/criteria exist on disk
  - case-id starts with a known skill name (routing-<skill> or <skill>-<behavior>)
  - domain directory is one of the known coarse domains
  - case-id unique across domains

Exit codes: 0 clean (warnings allowed) · 1 errors found · 2 usage error.
`--strict` escalates warnings to errors (skill-lint pattern).

Usage:
    python3 tools/eval-lint.py [--root evals] [--strict]
"""

import argparse
import os
import re
import sys

KNOWN_DOMAINS = {"code", "data", "media", "system", "web", "process"}
SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "skills")
FIXTURE_RE = re.compile(r"fixtures/[\w][\w\-./]*")


def known_skills():
    try:
        return {d for d in os.listdir(SKILLS_DIR)
                if os.path.isfile(os.path.join(SKILLS_DIR, d, "SKILL.md"))}
    except OSError:
        return set()


def referenced_fixtures(text):
    """Fixture paths mentioned in prose, with trailing punctuation stripped."""
    hits = []
    for m in FIXTURE_RE.findall(text):
        hits.append(m.rstrip(".,);:`'\""))
    return hits


def lint_case(case_dir, skills):
    errors, warnings = [], []

    def rel(p):
        return os.path.relpath(p, case_dir)

    prompt = os.path.join(case_dir, "prompt.md")
    criteria = os.path.join(case_dir, "graders", "criteria.md")

    if not os.path.isfile(prompt):
        errors.append(f"{rel(prompt)} missing")
    elif os.path.getsize(prompt) == 0:
        errors.append(f"prompt.md empty")
    if not os.path.isfile(criteria):
        errors.append(f"{rel(criteria)} missing")
    elif os.path.getsize(criteria) == 0:
        errors.append(f"graders/criteria.md empty")

    case_id = os.path.basename(case_dir)
    if not any(case_id == s or case_id.startswith(s + "-")
               or (case_id.startswith("routing-") and case_id[len("routing-"):] == s)
               for s in skills):
        warnings.append(f"case id `{case_id}` does not reference a known skill")

    if os.path.isfile(prompt) and os.path.isfile(criteria):
        with open(prompt, encoding="utf-8", errors="replace") as fh:
            ptext = fh.read()
        with open(criteria, encoding="utf-8", errors="replace") as fh:
            ctext = fh.read()
        for ref in dict.fromkeys(referenced_fixtures(ptext) + referenced_fixtures(ctext)):
            target = os.path.normpath(os.path.join(case_dir, ref))
            if not os.path.exists(target):
                errors.append(f"referenced fixture `{ref}` does not exist")

    return errors, warnings


def main() -> int:
    ap = argparse.ArgumentParser(description="Lint evals/ case structure.")
    ap.add_argument("--root", default=os.path.join(os.path.dirname(__file__), "..", "evals"),
                    help="evals root (default: repo evals/)")
    ap.add_argument("--strict", action="store_true",
                    help="treat warnings as errors")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"error: evals root not found: {root}", file=sys.stderr)
        return 2

    skills = known_skills()
    total_errors = total_warnings = 0
    seen_cases = {}

    for domain in sorted(os.listdir(root)):
        dom_path = os.path.join(root, domain)
        if domain.startswith(".") or not os.path.isdir(dom_path):
            continue
        if domain in ("graders", "__pycache__"):
            continue
        if domain not in KNOWN_DOMAINS:
            print(f"warning: unknown evals domain `{domain}/` "
                  f"(known: {', '.join(sorted(KNOWN_DOMAINS))})")
            total_warnings += 1
        for case_id in sorted(os.listdir(dom_path)):
            case_dir = os.path.join(dom_path, case_id)
            if not os.path.isdir(case_dir) or case_id.startswith("."):
                continue
            if case_id in seen_cases:
                print(f"error: duplicate case id `{case_id}` "
                      f"(also under {seen_cases[case_id]}/)")
                total_errors += 1
                continue
            seen_cases[case_id] = domain
            errors, warnings = lint_case(case_dir, skills)
            for e in errors:
                print(f"error: {os.path.relpath(case_dir, root)}: {e}")
            for w in warnings:
                print(f"warning: {os.path.relpath(case_dir, root)}: {w}")
            total_errors += len(errors)
            total_warnings += len(warnings)

    n_cases = len(seen_cases)
    verdict = f"eval-lint: {total_errors} error(s); {total_warnings} warning(s); {n_cases} case(s)"
    if total_errors or (args.strict and total_warnings):
        print(verdict)
        return 1
    print(verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
