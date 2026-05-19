import os
import io
import cv2
import base64
import requests
import numpy as np
import fal_client

from PIL import Image
from dotenv import load_dotenv
from fastapi import HTTPException

from services import Image_Prompt_service
from schemas.Prompt_Schema import PromptRequest


load_dotenv()

ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID2")
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN2")

API_URL = (
    f"https://api.cloudflare.com/client/v4/accounts/"
    f"{ACCOUNT_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell"
)

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}


# Generate image using Cloudflare
def generate_image(data: str, file=None):
    try:
        enhanced_prompt = Image_Prompt_service.generate_prompt(data)

        response = requests.post(
            API_URL,
            headers=HEADERS,
            json={"prompt": enhanced_prompt["prompt"]},
            timeout=30
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Cloudflare API error: {response.text}"
            )

        result = response.json()

        if "result" not in result or "image" not in result["result"]:
            raise HTTPException(
                status_code=500,
                detail="Invalid response from API"
            )

        base_img = Image.open(
            io.BytesIO(base64.b64decode(result["result"]["image"]))
        ).convert("RGB")

        logo_img = None

        if file:
            file.file.seek(0)
            logo_img = Image.open(file.file).convert("RGBA")

        final_img = (
            smart_logo_placement(base_img, logo_img)
            if logo_img else base_img
        )

        buffer = io.BytesIO()
        final_img.save(buffer, format="PNG")

        return {
            "status": "success",
            "image": base64.b64encode(buffer.getvalue()).decode()
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Generate image-to-image using Fal AI
def generate_image_to_image(data: PromptRequest):
    if not data.image_url:
        raise HTTPException(
            status_code=400,
            detail="image_url is required"
        )

    def on_queue_update(update):
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                print(log["message"])

    result = fal_client.subscribe(
        "fal-ai/flux/dev/image-to-image",
        arguments={
            "image_url": data.image_url,
            "prompt": data.user_prompt
        },
        with_logs=True,
        on_queue_update=on_queue_update,
    )

    return {
        "type": "image-to-image",
        "data": result
    }


# Find low detail regions
def find_low_detail_regions(image: Image.Image):
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    return 255 - edges


# Find best logo position
def get_best_position(score_map, box_size=150, step=20):
    h, w = score_map.shape

    best_score = -1
    best_pos = (0, 0)

    for y in range(0, h - box_size, step):
        for x in range(0, w - box_size, step):
            region = score_map[y:y + box_size, x:x + box_size]
            score = np.mean(region)

            if score > best_score:
                best_score = score
                best_pos = (x, y)

    return best_pos


# Resize logo
def resize_logo(logo: Image.Image, base_img: Image.Image):
    base_w, _ = base_img.size

    target_width = int(base_w * 0.15)
    aspect_ratio = logo.height / logo.width
    target_height = int(target_width * aspect_ratio)

    return logo.resize((target_width, target_height))


# Blend logo into image
def blend_logo(base_img: Image.Image, logo: Image.Image, position):
    if logo.mode != "RGBA":
        logo = logo.convert("RGBA")

    alpha = logo.split()[3]
    alpha = alpha.point(lambda p: int(p * 0.85))

    logo.putalpha(alpha)

    base_img.paste(logo, position, logo)

    return base_img


# Smart logo placement
def smart_logo_placement(base_img: Image.Image, logo_img: Image.Image):
    score_map = find_low_detail_regions(base_img)

    position = get_best_position(score_map)

    resized_logo = resize_logo(logo_img, base_img)

    return blend_logo(base_img, resized_logo, position)