---
description: Run ruff and pytest, then summarize any failures with their likely cause
---

Run these from the project root, in order:

1. `uv run ruff check .`
2. `uv run pytest -q`

Then report:

- One line per tool: pass or fail, with counts.
- For each failure: the file and line, the error type, and the most likely cause in one or two sentences. Point to the specific code that needs to change.
- If a failure comes from a rule in `CLAUDE.md` (for example, a node returning the whole state), name the rule.

Do not fix anything unless I ask. Do not run `playground.py` or `evals/run_evals.py`.

$ARGUMENTS
