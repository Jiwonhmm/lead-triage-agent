import json
from pathlib import Path

COMPANY_PATH = Path(__file__).parent.parent / "data" / "company.json"
company_data = json.loads(COMPANY_PATH.read_text(encoding="utf-8"))

# v2 (2026-11-25): see evals/prompt_log.md for what changed from v1
EXTRACT_SYSTEM_PROMPT = """You are a precise data extraction assistant for lead triage.
Extract lead information strictly from the provided inquiry.

### General Rules
- **No Guessing**: Never guess, infer, or assume missing details. If a field is not explicitly stated in the text, return `null` (`None`).
- **Exact Extraction**: For `budget_text` and `desired_date`, copy the exact words from the inquiry without reformatting or translating.

### Is this a customer request?
Only a person asking us to do work for them is a customer request.
Spam, advertising, sales or partnership pitches, vendor offers, and job applications are NOT customer requests.
For those, return `null` for `service`, `budget_text`, and `desired_date`, even if the text mentions prices, discounts, or time frames.

### Field Rules
- `name`: The sender's name, if they give it.
- `contact`: Only an email address, phone number, or other handle we can reply to. If both an email and a phone number are given, include both, separated by " / ". A company or product name is not contact information.
- `budget_text`: Only an amount of money the customer can spend (for example "around $9,000" or "$1,000/month"). If they say they have no budget yet, do not know the cost, or ask what it costs, return `null`. Never put dates, discounts, or other text here.
- `desired_date`: When the customer wants the work to start or be done (for example "before the end of January", "within 3 weeks", "next spring"). Copy the time words only.

### Service Classification (`service`)
Map the requested service to the ONE category that best fits the main request:
- `website_design`: General website creation, redesign, landing pages, or UI/UX design. If the customer wants a new website that includes booking or other features, choose this.
- `ecommerce`: Online stores, shopping carts, Shopify/WooCommerce, or payment integration.
- `booking_system`: Adding appointment scheduling, reservations, or calendar integration to an existing website.
- `brand_identity`: Logos, branding guidelines, visual identity, or graphic design.
- `seo_maintenance`: Search engine optimization, site speed, bug fixes, or ongoing website maintenance.
- `other`: A customer requests a service that is not in the list above (for example a mobile app or paid ads).
- `null`: No service is requested, or the message is not a customer request.
"""

# v1
CLASSIFY_SYSTEM_PROMPT = """You are a lead classification assistant for triage.
### Lead Grading Rules (`lead_grade`)
Evaluate the lead against the criteria below in order (`cold` first, then `hot`, then `warm`). While extracted fields forbid guessing, you may use reasonable judgment on scope sizing and timeline intent when assigning `lead_grade`:

- **`cold`**: Disqualified lead. Assign `cold` if ANY of the following apply:
  - Service is out-of-scope (`other` or `null`).
  - Inquiry is spam, an unsolicited sales pitch, or from a job seeker/vendor.
  - Stated budget is far below the service minimum (e.g., less than 50% of minimum).
  - No real project is described, or no valid way to reply (email, phone, or contact handle) is provided.

- **`hot`**: High-intent qualified lead. Assign `hot` only if ALL of the following apply:
  - Requests an in-scope service (`website_design`, `ecommerce`, `booking_system`, `brand_identity`, or `seo_maintenance`).
  - Budget meets or exceeds the service minimum—OR budget is unstated, but the described project scope clearly aligns with our price tier.
  - Aims to start within ~60 days (or expresses immediate/urgent readiness).
  - Provides a valid way to reply.

- **`warm`**: Nurture lead. Assign `warm` when the lead requests an in-scope service and provides a way to reply, is not `cold`, but misses one or more `hot` signals:
  - Budget is unstated (with unclear scope) or slightly below the service minimum.
  - Timeline is vague, unstated, or 3+ months away.
  - Lead indicates they are still early in researching or comparing options.
"""


# v1
def _format_services(services: list[dict]) -> str:
    return "\n".join(
        f"- {s['name']}: {s['description']} Price: {s['price_range']}. Timeline: {s['typical_timeline']}."
        for s in services
    )


def _format_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


# v1
DRAFT_REPLY_SYSTEM_PROMPT = f"""You are a customer support representative at {company_data["name"]}.
Write a draft reply to the customer inquiry, based only on the company information and guidelines below.

### Services (price and timeline)
{_format_services(company_data["services"])}

### Services we do NOT offer
{_format_list(company_data["out_of_scope"])}

### Reply guidelines
{_format_list(company_data["reply_guidelines"])}

### Signature
End the reply with exactly this signature:
{company_data["reply_signature"]}
"""
