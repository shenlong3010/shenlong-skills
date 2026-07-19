# Pass criteria — routing-symbol-lookup

1. The definition is located correctly: `fixtures/config.py`, the `def parse_config` line.
2. Both call sites are reported: one in `fixtures/app.py`, one in `fixtures/config.py` (`reload`).
3. Routing: the run treats this as a symbol question — definition/reference distinction is explicit (not just raw grep lines dumped). Use of the symbol-lookup lane (ctags/ast-grep, or Grep with definition-pattern anchors like `^def parse_config`) counts; pasting every textual occurrence of the string `parse_config` without classifying def vs call fails this criterion.
4. Output does not exceed a screenful — no full-file dumps.
