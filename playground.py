import json
from app.graph import graph

leads = json.load(open("data/sample_leads.json"))
for i in [0, 6, 13, 19]:
    result = graph.invoke({"raw_text": leads[0]["raw_text"]})
    print(result.get("reply_draft"))