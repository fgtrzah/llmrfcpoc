from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class PromptMessageDTO(BaseModel):
    id: int
    name: str = "John Doe"
    signup_ts: Optional[datetime] = None


PromptMessageListDTO = List[PromptMessageDTO]
