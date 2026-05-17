"""
API ROUTER
GET /marketing/campaigns?business_type=...&region=...
"""

import traceback
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from pipeline import run_pipeline
from schemas.agents_schema import Campaign,CampaignBrief,PipelineResponse
from schemas.ResponseSchema import RequestSchema
import os
from dotenv import load_dotenv
from fastapi import UploadFile, File, Form,Depends

load_dotenv()

agents_router = APIRouter(prefix="/marketing", tags=["Marketing Intelligence"])



def get_request_data(
    business_type: str = Form(...),
    region: str = Form(...),
) -> RequestSchema:
    return RequestSchema(
        business_type = business_type,
        region=region
    )





@agents_router.post("/campaigns")
def generate_campaigns(
    data : RequestSchema = Depends(get_request_data),
    file: UploadFile = File(None)
):
    if not os.getenv("SERP_API_KEY"):
        raise HTTPException(status_code=500, detail="SERP_API_KEY not configured.")
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured.")

    try:
        print("file : ",file)
        result = run_pipeline(business_type=data.business_type, region=data.region,file=file)
    except Exception as e:
        # Return full traceback so you can see exactly where it failed
        raise HTTPException(status_code=500, detail=f"{str(e)}\n\n{traceback.format_exc()}")

    if "error" in result:
        raise HTTPException(status_code=422, detail=result["error"])

    return result