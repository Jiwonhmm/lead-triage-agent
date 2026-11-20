import uuid
from langchain_core.messages import AIMessage
from langgraph.types import Command

from app import nodes
from app.graph import graph
from app.schemas import ExtractedLead, Classification


class FakeLLM:
    def __init__(self, answer):
        self.answer = answer

    def invoke(self, messages):
        return self.answer


FAKE_LEAD = ExtractedLead(
    name="Test", contact="test@example.com", service="website_design",
    budget_text="$9,000", desired_date="January",
)


def use_fake_llms(monkeypatch, grade):
    """LLM 3개를 가짜로 바꾸고, classify가 grade를 답하게 한다."""
    monkeypatch.setattr(nodes, "extract_llm", FakeLLM(FAKE_LEAD))
    monkeypatch.setattr(nodes, "classify_llm", FakeLLM(Classification(reason="test", grade=grade)))
    monkeypatch.setattr(nodes, "llm", FakeLLM(AIMessage(content="Hi, this is a draft.")))


def new_config():
    return {"configurable": {"thread_id": str(uuid.uuid4())}}   # 테스트마다 새 사물함


def test_hot_lead_pauses_for_approval(monkeypatch):
    use_fake_llms(monkeypatch, "hot")
    config = new_config()

    graph.invoke({"raw_text": "anything"}, config)

    state = graph.get_state(config)
    assert state.next == ("human_approval",)                   # 어디서 멈춰야 하나요?
    assert state.values["reply_draft"] == "Hi, this is a draft."       # 가짜 llm이 준 글


def test_warm_lead_finishes_without_approval(monkeypatch):
    use_fake_llms(monkeypatch, "warm")
    config = new_config()

    result = graph.invoke({"raw_text": "anything"}, config)

    assert graph.get_state(config).next == ()   # 멈춘 곳이 없으면?
    assert "reply_draft" not in result             # 초안을 안 써야 해요


def test_hot_lead_rejected_is_not_sent(monkeypatch):
    use_fake_llms(monkeypatch, "hot")
    config = new_config()

    graph.invoke({"raw_text": "anything"}, config)          # 1) 멈춤까지
    result = graph.invoke(Command(resume={"action": "rejected"}), config)     # 2) 거절하고 이어가기

    assert result["approval"] == "rejected"
    assert graph.get_state(config).next == ()         # 끝났으니 멈춘 곳 없음