import json
from langgraph.types import Command
from app.graph import graph

leads = json.load(open("data/sample_leads.json"))
config = {"configurable": {"thread_id": "lead-001-c"}}

# 1) 실행 → human_approval에서 멈춤
graph.invoke({"raw_text": leads[0]["raw_text"]}, config)

# 2) 멈춘 상태 확인
state = graph.get_state(config)
print("next:", state.next)
print(state.values["reply_draft"])

# 3) 승인하고 이어가기
# result = graph.invoke(Command(resume={"action": "modify"}), config)
Command(resume={"action": "modify", "reply_draft": "Hi Sarah, thanks! Let's book a call. Best, The Brightwave Team"})
print("approval:", result["approval"])