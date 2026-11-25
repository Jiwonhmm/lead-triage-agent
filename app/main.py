import os
import secrets
import uuid

from fastapi import Depends, FastAPI, Header, HTTPException
from langgraph.types import Command

from app.graph import graph
from app.schemas import ApproveRequest, LeadRequest
from app.tracing import tracing_callbacks

app = FastAPI(title="Lead Triage Agent")


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Block requests without the right X-API-Key header.

    Only active when API_ACCESS_KEY is set (in the deployed server).
    Locally and in tests it is not set, so every request is allowed.
    """
    expected = os.getenv("API_ACCESS_KEY")
    if not expected:
        return
    if x_api_key is None or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/health")
async def health():
    """Used by the load balancer to check that the server is up. No API key needed."""
    return {"status": "ok"}


def make_config(thread_id: str) -> dict:
    return {
        "configurable": {"thread_id": thread_id},
        "callbacks": tracing_callbacks(),  # one Langfuse trace per request (if enabled)
        "run_name": "lead-triage",
    }


@app.post("/leads", dependencies=[Depends(require_api_key)])
async def create_lead(body: LeadRequest):
    thread_id = str(uuid.uuid4())  # 문의마다 새 사물함 번호
    await graph.ainvoke({"raw_text": body.raw_text}, make_config(thread_id))
    return {"thread_id": thread_id}


@app.get("/leads/{thread_id}", dependencies=[Depends(require_api_key)])
async def get_lead(thread_id: str):
    snapshot = await graph.aget_state(make_config(thread_id))
    if not snapshot.values:  # 저장된 게 없으면
        raise HTTPException(status_code=404, detail="Lead not found")
    return {
        "thread_id": thread_id,
        "waiting_for_approval": "human_approval" in snapshot.next,
        "grade": snapshot.values.get("grade"),
        "reply_draft": snapshot.values.get("reply_draft"),
        "approval": snapshot.values.get("approval"),
    }


@app.post("/leads/{thread_id}/approve", dependencies=[Depends(require_api_key)])
async def approve_lead(thread_id: str, body: ApproveRequest):
    result = await graph.ainvoke(Command(resume=body.model_dump()), make_config(thread_id))
    return {"thread_id": thread_id, "approval": result.get("approval")}
