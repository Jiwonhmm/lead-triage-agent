from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from app.nodes import (
    classify,
    draft_reply,
    extract,
    human_approval,
    log_only,
    route_after_approval,
    route_by_grade,
    schedule_followup,
    send,
)
from app.state import AgentState

# ① 빈 그래프 만들기: 이 그래프는 AgentState를 쓴다
builder = StateGraph(AgentState)

# ② 노드 등록: ("노드 이름", 실행할 함수)
builder.add_node("extract", extract)
builder.add_node("classify", classify)
builder.add_node("draft_reply", draft_reply)
builder.add_node("schedule_followup", schedule_followup)
builder.add_node("log_only", log_only)
builder.add_node("human_approval", human_approval)
builder.add_node("send", send)

# ③ 선 잇기: (출발, 도착)
builder.add_edge(START, "extract")
builder.add_edge("extract", "classify")
builder.add_conditional_edges("classify", route_by_grade)  # 분기 1: 등급
builder.add_edge("draft_reply", "human_approval")

builder.add_conditional_edges(
    "human_approval", route_after_approval, {"send": "send", "end": END}
)  # 분기 2: 승인 결과

builder.add_edge("send", END)
builder.add_edge("schedule_followup", END)
builder.add_edge("log_only", END)

# ④ 실행할 수 있는 그래프로 만들기
graph = builder.compile(checkpointer=InMemorySaver())
