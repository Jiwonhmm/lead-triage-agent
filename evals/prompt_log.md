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

## extract v2 (2026-11-25)

Based on the v1 eval run (20 leads): classification 100%, extraction 88%. 12 field failures.

**What failed in v1, by cause**
| Cause | Leads | Fields |
| --- | --- | --- |
| "No budget yet" text extracted as a budget | 007, 009, 011, 013 | budget_text |
| Spam and vendor pitches treated as customer requests | 014, 018 | service, budget_text, desired_date, contact |
| Wrong field: "probably in February" put in budget, date left empty | 013 | budget_text, desired_date |
| Service ambiguity: new website with booking, job application | 011, 016 | service |

**What changed**
- Added a "Is this a customer request?" rule: spam, pitches, vendor offers, and job applications get `null` for service, budget, and date.
- Defined each field: `budget_text` is only an amount of money; "no budget" or "how much does it cost" is `null`. `contact` is only an email, phone, or handle, and includes both email and phone when both are given. A company name is not contact information.
- Service: a new website that includes booking is `website_design`; `booking_system` is for adding booking to an existing site. `other` is only for customer requests outside our services; non-requests are `null`.

The eval dataset was not changed between v1 and v2, so the scores compare the same answers.

**Expected to fix:** 007, 009, 011, 013, 014, 016, 018.

**Result (2026-11-25):** classification 100%, extraction **94%** (v1: 88%). Field failures went from 12 to 6.

| Field | v1 | v2 |
| --- | --- | --- |
| name | 100% | 95% |
| contact | 95% | 95% |
| service | 80% | 90% |
| budget_text | 75% | 95% |
| desired_date | 90% | 95% |

- Fixed: 007, 009, 013, 014, 016 (budget wording, spam, job application, wrong field).
- Still wrong: lead-011 `service` (Korean inquiry, new website with booking) is still `booking_system`.
- New problem: lead-018 (vendor pitch). The model returned the **string** `"null"` instead of a real null for name, contact, budget_text, and desired_date, and `other` for service. 4 of the 6 v2 failures come from this one lead. It also made `name` worse (the sender's name "Michael" was dropped).

**Candidates for v3**
- Normalize the string values "null", "none", and "" to a real `None` in code (a Pydantic validator), instead of hoping the prompt prevents it. This is a deterministic fix and can be unit-tested.
- Tell the model that `name` and `contact` should still be extracted for non-customer messages, if the sender gives them.

---

## Eval results

Filled in after `evals/run_evals.py` runs on all 20 labeled leads.

| Version | Classification accuracy | Extraction accuracy | Notes |
| --- | --- | --- | --- |
| Version | Classification accuracy | Extraction accuracy | Notes |
| --- | --- | --- | --- |
| v1 | 100% | 88% | Baseline |
| v2 | 100% | 94% | Customer-request rule, field definitions, service rules |
