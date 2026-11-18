#노드 함수 만들기
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from app.schemas import ExtractedLead, Classification
from app.state import AgentState
from app.prompts import EXTRACT_SYSTEM_PROMPT, CLASSIFY_SYSTEM_PROMPT, DRAFT_REPLY_SYSTEM_PROMPT
from langgraph.types import interrupt 


load_dotenv()

# 모델은 함수 밖에, 파일 위쪽에 한 번만 필요하다
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
extract_llm = llm.with_structured_output(ExtractedLead)
classify_llm = llm.with_structured_output(Classification)

# 노드 함수
def extract(state: AgentState) -> dict:
    """
    Extract lead information from the raw text in the state.
    """
    raw_text = state["raw_text"]
    
    # LLM 호출
    result = extract_llm.invoke([
        ("system", EXTRACT_SYSTEM_PROMPT),
        ("human", raw_text)
    ])
    
    return {"extracted": result}


#classification 노드 함수
def classify(state: AgentState) -> dict:
    """
    Classify the lead based on the extracted information in the state.
    """
    raw_text = state["raw_text"]
    extracted = state["extracted"]
    
    # LLM 호출
    result = classify_llm.invoke([
        ("system", CLASSIFY_SYSTEM_PROMPT),
        ("human", f"Raw text: {raw_text}\nExtracted lead information: {extracted.model_dump_json()}")
    ])
    
    return {"grade": result.grade, "grade_reason": result.reason}



def draft_reply(state: AgentState) -> dict:
    """
    Draft a reply based on the lead's grade and extracted information.
    """
    raw_text = state["raw_text"]
    extracted = state["extracted"]

    result  = llm.invoke([
        ("system", DRAFT_REPLY_SYSTEM_PROMPT),
        ("human", f"Raw text: {raw_text}\nExtracted lead information: {extracted.model_dump_json()}\nClassification: {state['grade']} - {state['grade_reason']}")
    ])

    return {"reply_draft": result.content}

    
def schedule_followup(state: AgentState) -> dict:
    """
    Schedule a follow-up based on the lead's grade and extracted information.
    """
    print("Scheduling follow-up...")
    return {}


def log_only(state: AgentState) -> dict:
    """
    Log the lead information without taking any further action.
    """
    print("Logging lead information...")
    return {}


def route_by_grade(state : AgentState) -> str:
    """
    Route the lead to the appropriate action based on its grade.
    """
    grade = state.get("grade")
    if grade == "hot":
        return "draft_reply"
    elif grade == "warm":
        return "schedule_followup"
    elif grade == "cold":
        return "log_only"
    else:
        raise ValueError(f"Unknown grade: {grade}")


# HITL
def human_appoval(state: AgentState) -> dict:
    """
    Human-in-the-loop approval for the lead classification.
    """
    decision = interrupt({"reply_draft": state["reply_draft"]})
    print("Requesting human approval...")
    return {}
