from langgraph.graph import StateGraph, START, END
from app.state import AgentState
from app.nodes import extract, classify, draft_reply, schedule_followup, log_only, route_by_grade


# ① 빈 그래프 만들기: 이 그래프는 AgentState를 쓴다
builder = StateGraph(AgentState)

# ② 노드 등록: ("노드 이름", 실행할 함수)
builder.add_node("extract", extract)
builder.add_node("classify", classify)
builder.add_node("draft_reply", draft_reply)
builder.add_node("schedule_followup", schedule_followup)
builder.add_node("log_only", log_only)

# ③ 선 잇기: (출발, 도착)
builder.add_edge(START, "extract")
builder.add_edge("extract", "classify")
builder.add_conditional_edges("classify", route_by_grade)
builder.add_edge("draft_reply", END)
builder.add_edge("schedule_followup", END)
builder.add_edge("log_only", END)

# ④ 실행할 수 있는 그래프로 만들기
graph = builder.compile()