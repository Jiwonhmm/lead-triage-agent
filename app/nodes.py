#노드 함수 만들기
from dotevn import load_dotenv
from langchain_openai import ChatOpenAI
from app.schemas import ExtractedLead
from app.state import AgentState
from app.schemas import ExtractedLead

load_dotenv()

# 모델은 함수 밖에, 파일 위쪽에 한 번만 필요하다
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
extract_llm = llm.with_structured_output(ExtractedLead)

# 노드 함수