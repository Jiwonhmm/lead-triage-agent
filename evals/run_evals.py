"""
Run the labeled eval set against the real LLM and print accuracy.

Usage (from the project root):
    uv run python -m evals.run_evals v1
"""

import json
import sys
from pathlib import Path

from app.nodes import classify, extract

ROOT = Path(__file__).parent.parent
FIELDS = ["name", "contact", "service", "budget_text", "desired_date"]


# ---------- 채점 규칙 (dataset.json의 "rules"와 같은 내용) ----------

def match_exact(expected, actual):
    """name, service: 대소문자 무시하고 정확히 같아야 맞음. null이면 비어 있어야 맞음."""
    if expected is None:
        return actual is None
    return actual is not None and expected.lower() == actual.lower()


def match_contact(expected_pieces, actual):
    """contact: 정답 조각이 전부 들어 있어야 맞음. 빈 목록이면 비어 있어야 맞음."""
    if not expected_pieces:
        return actual is None
    return actual is not None and all(p.lower() in actual.lower() for p in expected_pieces)


def match_contains(expected, actual):
    """budget_text, desired_date: 정답 글자가 안에 들어 있으면 맞음."""
    options = expected if isinstance(expected, list) else [expected]
    for option in options:
        if option is None and actual is None:
            return True
        if option is not None and actual is not None and option.lower() in actual.lower():
            return True
    return False


def match_field(field, expected, actual):
    if field == "contact":
        return match_contact(expected, actual)
    if field in ("budget_text", "desired_date"):
        return match_contains(expected, actual)
    return match_exact(expected, actual)


# ---------- 실행 ----------

def main():
    version = sys.argv[1] if len(sys.argv) > 1 else "unlabeled"

    dataset = json.loads((ROOT / "evals" / "dataset.json").read_text(encoding="utf-8"))
    leads = json.loads((ROOT / "data" / "sample_leads.json").read_text(encoding="utf-8"))
    raw_by_id = {lead["id"]: lead["raw_text"] for lead in leads}

    grade_correct = 0
    field_correct = {field: 0 for field in FIELDS}
    failures = []

    for item in dataset["items"]:
        lead_id = item["id"]
        state = {"raw_text": raw_by_id[lead_id]}

        # 1) 진짜 LLM으로 추출과 분류
        extracted = extract(state)["extracted"]
        classified = classify({**state, "extracted": extracted})

        # 2) 등급 채점
        if classified["grade"] == item["expected_grade"]:
            grade_correct += 1
        else:
            failures.append(f"{lead_id} grade: expected {item['expected_grade']}, got {classified['grade']}")

        # 3) 필드 채점
        for field in FIELDS:
            expected = item["expected"][field]
            actual = getattr(extracted, field)
            if match_field(field, expected, actual):
                field_correct[field] += 1
            else:
                failures.append(f"{lead_id} {field}: expected {expected!r}, got {actual!r}")

        print(f"done {lead_id}")

    # 4) 결과 출력
    total = len(dataset["items"])
    print(f"\n=== Eval results ({version}) ===")
    print(f"Classification accuracy: {grade_correct}/{total} = {grade_correct / total:.0%}")
    for field in FIELDS:
        print(f"  {field:13} {field_correct[field]}/{total} = {field_correct[field] / total:.0%}")
    overall = sum(field_correct.values()) / (total * len(FIELDS))
    print(f"Extraction accuracy (all fields): {overall:.0%}")

    print("\nFailures:")
    for line in failures:
        print(" -", line)


if __name__ == "__main__":
    main()