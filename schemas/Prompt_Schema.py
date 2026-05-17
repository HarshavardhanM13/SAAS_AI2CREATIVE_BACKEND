from pydantic import BaseModel
from typing import Optional

class PromptRequest(BaseModel):
    user_prompt : str
    user_style : str
    image_url: Optional[str] = None