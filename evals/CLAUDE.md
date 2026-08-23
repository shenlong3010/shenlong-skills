# evals/ — directory guide

Golden regression cases in the native `claude plugin eval` layout. One directory per case; nothing else lives here.

## Case anatomy

```
evals/<domain>/<case-id>/
├── prompt.md          # the exact user prompt — self-contained, no session context assumed
└── graders/
    └── criteria.md    # what a correct response must do / must not do
```

- `<domain>` is coarse: `code`, `data`, `media`, `system`, `web` (add one only when nothing fits).
- `<case-id>` is either `routing-<skill>` (does the right skill lane fire?) or `<skill>-<behavior>` (does the skill's gotcha hold under adversarial input?).
- Fixtures ship inside the case directory when the prompt references them.

Authoring goes through `/eval-writer` (it owns extraction from run traces); author by hand only when porting an obvious case. Run: `claude plugin eval shenlong-skills --tag routing --runs 1`.
