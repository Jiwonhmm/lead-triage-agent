---
description: Record a prompt change in evals/prompt_log.md
---

A prompt in `app/prompts.py` was just changed. Record it in `evals/prompt_log.md`.

1. Run `git diff app/prompts.py` to see what changed.
2. Check that the changed prompt's `#vN` comment was bumped. If not, tell me and stop.
3. Add a new section to `evals/prompt_log.md`, following the format of the existing sections:
   - Heading: `## <prompt name> vN (<today's date>)`
   - What failed in the previous version (link to the earlier section's table rows if they exist).
   - What changed, in plain words.
   - Which leads the change is expected to fix.
   - Leave the score as TBD until evals are run.
4. Show me the new section before saving it.

Extra notes from me: $ARGUMENTS
