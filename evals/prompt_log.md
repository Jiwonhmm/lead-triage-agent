# Prompt Log

A record of each prompt version: what went wrong, what changed, and how the scores moved.
The before/after table in the README is copied from this file.

Prompt versions here match the `#v1`, `#v2` comments in `app/prompts.py`.

---

## extract v1 (2026-11-16)

Manual check on 4 sample leads (lead-001, 007, 014, 020). No eval score yet.

| Lead | Field | Output | Expected | Cause |
| --- | --- | --- | --- | --- |
| lead-001 | contact | Email only (varies between runs) | Email and phone | No rule for when both are given |
| lead-007 | budget_text | "not sure what it costs yet" | null | "Budget" is not defined |
| lead-014 | budget_text | "90% discount" | null | Numbers in a spam message read as a customer request |
| lead-014 | desired_date | "7 days" | null | Same as above |
| lead-014 | service | seo_maintenance | null or other | Same as above |

**Observations**
- lead-001 `contact` changed between runs even at `temperature=0`. Across the 6 runs so far, it returned email only 3 times and email + phone 3 times. Fields with vague rules produce unstable output.
- lead-020 (empty message) returned all fields as null, as expected.

**Candidates for v2**
- `contact`: if both email and phone are given, include both.
- `budget_text`: only an amount the customer can spend. "Not sure" or "TBD" is null.
- Sales pitches and spam are not customer requests, so `service`, `budget_text`, and `desired_date` are null.

---

## classify v1 (2026-11-16)

Manual check on the same 4 leads. All 4 grades matched the expected grade (hot, warm, cold, cold).

**Observations**
- lead-014 was graded cold even though extract got it wrong. Passing the raw text along with the extracted fields let classify catch the spam.
- lead-001 was graded hot partly because it "aims to start within 60 days". The model does not know today's date, so it cannot actually check this. The right answer here was luck.
- The prompt asks whether the budget meets the service minimum, but the minimum amounts are not in the prompt. The model is guessing the price tiers.
- lead-020 ("I submitted a request last week and nobody answered") is cold by the criteria, but it is really a complaint from an existing customer. A real business should not drop it. No grade covers this case.

**Candidates for v2**
- Pass `received_at` (the date the inquiry arrived) so the model can judge "within ~60 days".
- Add each service's minimum budget to the prompt (reuse `_format_services`).
- Consider a rule or separate route for follow-ups and complaints from existing customers. This may be a limitation to note in the README instead of a prompt fix.

---

## draft_reply v1 (2026-11-18)

Manual check: lead-001 run 4 times.

**Observations**
- All 4 drafts followed the reply guidelines: about 100 words, one service with price range (CAD 3,000-12,000) and timeline (4-8 weeks), a 20-minute intro call, no fixed price or discount, correct signature.
- Wording changed on every run at `temperature=0`. Only 2 of the 4 drafts mentioned the online booking the customer asked for.
- This variation is the reason the graph pauses at `human_approval` before anything is sent.

**Candidates for v2**
- Ask the reply to acknowledge each specific request in the inquiry (for example, both the redesign and the booking feature).

---

## Eval results

Filled in after `evals/run_evals.py` runs on all 20 labeled leads.

| Version | Classification accuracy | Extraction accuracy | Notes |
| --- | --- | --- | --- |
| v1 | TBD | TBD | Baseline |
| v2 | TBD | TBD | |
