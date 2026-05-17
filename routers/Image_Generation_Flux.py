from services import Image_gen_service
from fastapi import APIRouter
from routers.Image_Prompt_Gen_Router import prompt_router
import requests
import os
from schemas.Prompt_Schema import PromptRequest
from fastapi import UploadFile, File, Form

Image_gen_router = APIRouter(tags=['Image Generation'])








from fastapi import UploadFile, File, Form

from fastapi import UploadFile, File, Depends
from fastapi import Form, Depends
from schemas.Prompt_Schema import PromptRequest

def get_prompt_request(
    user_prompt: str = Form(...),
    user_style: str = Form(...),
    image_url: str = Form(None),
) -> PromptRequest:
    return PromptRequest(
        user_prompt=user_prompt,
        user_style=user_style,
        image_url=image_url
    )


@Image_gen_router.post("/generate-image")
async def generate_image(
    data: PromptRequest = Depends(get_prompt_request),
    file: UploadFile = File(None)
):
    return Image_gen_service.generate_image(data=data, file=file)

@Image_gen_router.post("/generate-image-image")
async def generate_image_to_image(
    user_prompt: str = Form(...),
    user_style: str = Form(...),
    file: UploadFile = File(None),
    image_url: str = Form(None)
):
    return Image_gen_service.generate_image_with_logo(
        user_prompt=user_prompt,
        user_style=user_style,
        file=file,
        image_url=image_url
    )