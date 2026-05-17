from fastapi import APIRouter, HTTPException
from services import Image_Prompt_service
from schemas.Prompt_Schema import PromptRequest



prompt_router = APIRouter(tags=["prompt_gen"])






@prompt_router.post("/generate-prompt")
async def generate_prompt(data: PromptRequest):
    return Image_Prompt_service.generate_prompt(data=data)