# State는 모든 노드가 같이 읽고 쓰는 공유 메모장
from typing import TypedDict, Literal
from app.schemas import ExtractedLead

class AgentState(TypedDict, total = False):
    raw_text:str
    extracted: ExtractedLead
    grade: Literal["hot","warm","cold"]
    grade_reason: str 
    reply_draft: str
    approval: Literal["approved","rejected","pending", "modify"]


  