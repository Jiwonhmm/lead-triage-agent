"""
Run the labeled eval set against the real LLM and print accuracy.

Usage (from the project root):
    uv run python -m evals.run_evals v1
"""

import json
import sys
from pathlib import Path

from langchain_core.runnables import RunnableLambda

from app.nodes import classify, extract
from app.tracing import flush_traces, record_score, tracing_callbacks

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


def extract_and_classify(state):
    """extract와 classify를 차례로 실행한다. 하나로 묶어야 트레이스 1개로 기록된다."""
    extracted = extract(state)["extracted"]
    classified = classify({**state, "extracted": extracted})
    return extracted, classified


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

        # 1) 진짜 LLM으로 추출과 분류 (Langfuse에는 문의 1건 = 트레이스 1개로 기록)
        callbacks = tracing_callbacks()
        extracted, classified = RunnableLambda(extract_and_classify).invoke(
            state,
            config={"callbacks": callbacks, "run_name": f"eval-{version}-{lead_id}"},
        )
        trace_id = callbacks[0].last_trace_id if callbacks else None
        lead_failures = []

        # 2) 등급 채점
        grade_ok = classified["grade"] == item["expected_grade"]
        if grade_ok:
            grade_correct += 1
        else:
            lead_failures.append(
                f"{lead_id} grade: expected {item['expected_grade']}, got {classified['grade']}"
            )

        # 3) 필드 채점
        lead_fields_ok = 0
        for field in FIELDS:
            expected = item["expected"][field]
            actual = getattr(extracted, field)
            if match_field(field, expected, actual):
                field_correct[field] += 1
                lead_fields_ok += 1
            else:
                lead_failures.append(f"{lead_id} {field}: expected {expected!r}, got {actual!r}")

        # 4) Langfuse에 점수 기록 (트레이싱이 꺼져 있으면 아무 일도 안 함)
        comment = "\n".join(lead_failures) or "all correct"
        record_score(trace_id, "grade_correct", 1 if grade_ok else 0, comment)
        record_score(trace_id, "extraction_accuracy", lead_fields_ok / len(FIELDS), comment)
        failures.extend(lead_failures)

        print(f"done {lead_id}")

    # 5) 결과 출력
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

    flush_traces()


if __name__ == "__main__":
    main()
