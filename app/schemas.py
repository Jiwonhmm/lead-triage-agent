#LLM에서 추출한 값 pydantic모델
from pydantic import BaseModel, Field
from typing import Literal

class ExtractedLead(BaseModel):
    name: str | None = Field(..., description="if you can't find in the description, don't guess or assume. The name of the lead" )
    contact: str | None = Field(..., description="if you can't find in the description, don't guess or assume. The contact information of the lead" )
    service: Literal["website_design", "ecommerce", "booking_system", "brand_identity", "seo_maintenance", "other"] | None = Field(..., description="if you can't find in the description, don't guess or assume. The service for which the lead was received. other is out of service, none is not specified")
    budget_text: str | None = Field(..., description="if you can't find in the description, don't guess or assume. The budget information of the lead. Extract it exactly as written in the description. Return null if it is not stated.")
    desired_date: str | None = Field(..., description="if you can't find in the description, don't guess or assume. The desired date for the service, and extract exactly from the description, don't change the format.")


class Classification(BaseModel):
    reason: str = Field(..., description="give the reasons for the classification based on companies standards in 2 sentences")
    grade: Literal["hot","warm","cold"] = Field(..., description="choose one of the three grades based on the company's standards. hot: high potential lead, warm: moderate potential lead, cold: low potential lead")