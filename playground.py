import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from app.schemas import ExtractedLead

load_dotenv()

#모델만들기
llm = ChatOpenAI(model ="gpt-4o-mini", temperature=0)
structured_llm = llm.with_structured_output(ExtractedLead)

leads = json.load(open("data/sample_leads.json"))
raw_text = leads[0]["raw_text"]

#invoke
result = structured_llm.invoke([("system", "문의에서 정보를 추출해. 문의에 없으면 추측하지 말고 null"), ("human", raw_text)])

print(result)