from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 🔥 load env first
load_dotenv()

from routers.trends_router import app as trends_router
from routers.Image_Prompt_Gen_Router import prompt_router
from routers.Image_Generation_Flux import Image_gen_router
from routers.agents_api import agents_router

app = FastAPI()

# Routers
app.include_router(prompt_router, prefix="/prompt_gen")
app.include_router(Image_gen_router, prefix="/image_gen")
app.include_router(trends_router, prefix="/trends")
app.include_router(agents_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)