from pydantic import BaseModel
from typing import Optional,List



class CampaignBrief(BaseModel):
    campaign_name: str
    headline: str
    body: str
    cta: str
    best_channel: str


class Campaign(BaseModel):
    trend: str
    image_prompt: str
    campaign_brief: CampaignBrief


class PipelineResponse(BaseModel):
    business_type: str
    region: str
    campaigns: list[Campaign]

