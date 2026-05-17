from schemas.Prompt_Schema import PromptRequest
from fastapi import HTTPException
from routers.Image_Prompt_Gen_Router import prompt_router
from pydantic import BaseModel
from services import Image_Prompt_service
import requests
import os
from dotenv import load_dotenv
import fal_client


# Load environment variables
load_dotenv()



ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID2")
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN2")

API_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell"

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}









# def generate_image(data: PromptRequest):
#     try:
#         enhanced_prompt = Image_Prompt_service.generate_prompt(data=data)
#         print(enhanced_prompt)
#         payload = {
#             "prompt": enhanced_prompt["prompt"]
#         }

#         response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)

#         if response.status_code != 200:
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"Cloudflare API error: {response.text}"
#             )

#         result = response.json()

#         if "result" not in result or "image" not in result["result"]:
#             raise HTTPException(status_code=500, detail="Invalid response from API")

#         image_base64 = result["result"]["image"]

#         return {
#             "status": "success",
#             "image": image_base64
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    


import io
import base64
import requests
from PIL import Image
from fastapi import HTTPException
from schemas.Prompt_Schema import PromptRequest


def generate_image(data: str, file=None):
    try:
        # 🔹 Step 1: Generate prompt (use schema directly)
        enhanced_prompt = Image_Prompt_service.generate_prompt(data)
        #print(enhanced_prompt)
        payload = {
            "prompt": enhanced_prompt["prompt"]
        }
#         payload = {
#             "prompt": """A modern, minimalist cake shop interior designed for premium social media marketing. A sleek high-gloss white countertop displays neatly arranged premium cakes and desserts with rich textures and subtle color variations.

# The background wall is clean, plain, and uncluttered, with a large clearly visible empty space intentionally reserved for branding or logo placement. No people, no unnecessary objects, and no visual distractions.

# Soft cinematic lighting with gentle shadows enhances depth and realism. The composition is balanced with strong focus on the product while maintaining negative space.

# Ultra realistic, high contrast, professional commercial photography, sharp focus, 4k resolution, Instagram ad style"""
#         }
        # 🔹 Step 2: Call Cloudflare API
        cf_response = requests.post(
            API_URL,
            headers=HEADERS,
            json=payload,
            timeout=30
        )

        if cf_response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Cloudflare API error: {cf_response.text}"
            )

        result = cf_response.json()

        if "result" not in result or "image" not in result["result"]:
            raise HTTPException(status_code=500, detail="Invalid response from API")

        # 🔹 Step 3: Decode base image
        image_base64 = result["result"]["image"]

        try:
            base_img = Image.open(
                io.BytesIO(base64.b64decode(image_base64))
            ).convert("RGB")
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to decode generated image")

        # 🔹 Step 4: Load logo (priority: file > URL)
        logo_img = None

        # 🔥 FILE (from upload)
        if file:
            try:
                file.file.seek(0)
                logo_img = Image.open(file.file).convert("RGBA")
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid uploaded image")
        print(logo_img)

        # 🔥 URL (from schema)
        # elif data.image_url:
        #     try:
        #         img_res = requests.get(
        #             data.image_url,
        #             headers={"User-Agent": "Mozilla/5.0"},
        #             timeout=10
        #         )

        #         if img_res.status_code != 200:
        #             raise HTTPException(status_code=400, detail="Failed to fetch image URL")

        #         if "image" not in img_res.headers.get("Content-Type", ""):
        #             raise HTTPException(status_code=400, detail="URL is not an image")

        #         logo_img = Image.open(io.BytesIO(img_res.content)).convert("RGBA")

        #     except Exception:
        #         raise HTTPException(status_code=400, detail="Invalid image URL")

        # 🔥 Step 5: Smart logo placement
        final_img = smart_logo_placement(base_img, logo_img) if logo_img else base_img

        # 🔹 Step 6: Convert to base64
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
    
    
    
    
    
def generate_image_to_image(data : PromptRequest):
    if not data.image_url:
        raise HTTPException(status_code=400, detail="image_url is required")

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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
import os
import io
from PIL import Image
from dotenv import load_dotenv

from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation

load_dotenv()

os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
os.environ['STABILITY_KEY'] = os.getenv("STABILITY_API_KEY")

stability_api = client.StabilityInference(
    key=os.environ['STABILITY_KEY'],
    verbose=True,
    engine="stable-diffusion-xl-1024-v1-0",
)

# import requests
# import io
# import base64
# from PIL import Image

# import io
# import base64
# import requests
# from PIL import Image


# def generate_image_to_image_stbl(user_prompt, user_style, file=None, image_url=None):
#     try:
#         # 🔹 Build prompt
#         prompt = f"{user_prompt}, style: {user_style}"

#         # 🔹 Get image (priority: file > URL)
#         if file:
#             init_image = Image.open(file.file).convert("RGB")

#         elif image_url:
#             response = requests.get(
#                 image_url,
#                 headers={"User-Agent": "Mozilla/5.0"}
#             )

#             if response.status_code != 200:
#                 return {"status": "error", "message": "Failed to fetch image"}

#             if "image" not in response.headers.get("Content-Type", ""):
#                 return {"status": "error", "message": "Invalid image URL"}

#             init_image = Image.open(io.BytesIO(response.content)).convert("RGB")

#         else:
#             return {"status": "error", "message": "No image provided"}

#         # 🔹 Call Stability API
#         answers = stability_api.generate(
#             prompt=prompt,
#             init_image=init_image,
#             start_schedule=0.7,
#             steps=30,
#             cfg_scale=7.5,
#             width=1024,
#             height=1024,
#             sampler=generation.SAMPLER_K_DPMPP_2M,
#         )

#         # 🔹 Extract result
#         for resp in answers:
#             for artifact in resp.artifacts:
#                 if artifact.type == generation.ARTIFACT_IMAGE:
#                     img = Image.open(io.BytesIO(artifact.binary))

#                     buffer = io.BytesIO()
#                     img.save(buffer, format="PNG")

#                     return {
#                         "status": "success",
#                         "image": base64.b64encode(buffer.getvalue()).decode()
#                     }

#         return {"status": "error", "message": "No image generated"}

#     except Exception as e:
#         return {"status": "error", "message": str(e)}



import io
import base64
import requests
import cv2
import numpy as np
from PIL import Image

# ================================
# 🔹 SMART LOGO PLACEMENT HELPERS
# ================================

def find_low_detail_regions(image: Image.Image):
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    score_map = 255 - edges
    return score_map


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


def resize_logo(logo: Image.Image, base_img: Image.Image):
    base_w, _ = base_img.size
    target_width = int(base_w * 0.15)

    aspect = logo.height / logo.width
    target_height = int(target_width * aspect)

    return logo.resize((target_width, target_height))


def blend_logo(base_img: Image.Image, logo: Image.Image, position):
    if logo.mode != "RGBA":
        logo = logo.convert("RGBA")

    alpha = logo.split()[3]
    alpha = alpha.point(lambda p: int(p * 0.85))
    logo.putalpha(alpha)

    base_img.paste(logo, position, logo)
    return base_img


def smart_logo_placement(base_img: Image.Image, logo_img: Image.Image):
    score_map = find_low_detail_regions(base_img)
    pos = get_best_position(score_map)
    logo_resized = resize_logo(logo_img, base_img)
    final_img = blend_logo(base_img, logo_resized, pos)
    return final_img


# ================================
# 🔹 MAIN FUNCTION (UPDATED)
# ================================

def generate_image_with_logo(user_prompt, user_style, file=None, image_url=None):
    try:
        # 🔹 Build prompt (NO init image usage)
        prompt = f"{user_prompt}, style: {user_style}"

        # 🔹 Load logo (ONLY for overlay)
        if file:
            logo_img = Image.open(file.file).convert("RGBA")

        elif image_url:
            response = requests.get(
                image_url,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            if response.status_code != 200:
                return {"status": "error", "message": "Failed to fetch image"}

            if "image" not in response.headers.get("Content-Type", ""):
                return {"status": "error", "message": "Invalid image URL"}

            logo_img = Image.open(io.BytesIO(response.content)).convert("RGBA")

        else:
            return {"status": "error", "message": "No logo provided"}

        # 🔥 IMPORTANT: NO init_image here
        answers = stability_api.generate(
            prompt=prompt,
            steps=30,
            cfg_scale=8.5,
            width=1024,
            height=1024,
            sampler=generation.SAMPLER_K_DPMPP_2M,
        )

        # 🔹 Extract generated image
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.type == generation.ARTIFACT_IMAGE:

                    base_img = Image.open(io.BytesIO(artifact.binary)).convert("RGB")

                    # 🔥 APPLY SMART LOGO PLACEMENT
                    final_img = smart_logo_placement(base_img, logo_img)

                    buffer = io.BytesIO()
                    final_img.save(buffer, format="PNG")

                    return {
                        "status": "success",
                        "image": base64.b64encode(buffer.getvalue()).decode()
                    }

        return {"status": "error", "message": "No image generated"}

    except Exception as e:
        return {"status": "error", "message": str(e)}