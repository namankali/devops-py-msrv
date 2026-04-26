from pydantic import BaseModel
from typing import Dict, List, Any
class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, Any]] = []
    