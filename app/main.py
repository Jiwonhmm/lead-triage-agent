import uuid
from fastapi import FastAPI, HTTPException
from langgraph.types import Command
from app.graph import graph
from app.schemas import LeadRequest, ApproveRequest   

app = FastAPI(title="Lead Triage Agent") 


def make_config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


@app.post("/leads")
async def create_lead(body: LeadRequest):
    thread_id = str(uuid.uuid4())                   # 문의마다 새 사물함 번호
    await graph.ainvoke({"raw_text": body.raw_text}, make_config(thread_id))
    return {"thread_id": thread_id}


@app.get("/leads/{thread_id}")
async def get_lead(thread_id: str):
    snapshot = await graph.aget_state(make_config(thread_id))
    if not snapshot.values:                         # 저장된 게 없으면
        raise HTTPException(status_code=404, detail="Lead not found")
    return {
        "thread_id": thread_id,
        "waiting_for_approval": "human_approval" in snapshot.next,
        "grade": snapshot.values.get("grade"),
        "reply_draft": snapshot.values.get("reply_draft"),
        "approval": snapshot.values.get("approval"),
    }


@app.post("/leads/{thread_id}/approve")
async def approve_lead(thread_id: str, body: ApproveRequest):
    result = await graph.ainvoke(Command(resume=body.model_dump()), make_config(thread_id))
    return {"thread_id": thread_id, "approval": result.get("approval")}