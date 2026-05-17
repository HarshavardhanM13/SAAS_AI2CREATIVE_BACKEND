

from pydantic import BaseModel
from typing import List, Optional


class ResponseStructure(BaseModel):
    pass

class RequestSchema(BaseModel):
    business_type : str
    region : str
    