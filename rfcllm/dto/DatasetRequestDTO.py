from typing import Optional
from pydantic import BaseModel


class DatasetRequestDTO(BaseModel):
    id: str
    ids: Optional[list[str]]
