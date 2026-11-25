import json
from langgraph.types import Command
from app.graph import graph
from app.tracing import flush_traces, tracing_callbacks

leads = json.load(open("data/sample_leads.json"))
config = {
    "configurable": {"thread_id": "lead-001-d"},
    "callbacks": tracing_callbacks(),
    "run_name": "playground-lead-001",
}

# 1) 실행 → human_approval에서 멈춤
graph.invoke({"raw_text": leads[0]["raw_text"]}, config)

# 2) 멈춘 상태 확인
state = graph.get_state(config)
print("next:", state.next)
print(state.values["reply_draft"])

# 3) 승인하고 이어가기
result = graph.invoke(Command(resume={"action": "approved"}), config)
print("approval:", result["approval"])

flush_traces()