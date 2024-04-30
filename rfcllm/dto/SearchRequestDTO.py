from typing import Optional
from pydantic import BaseModel


class SearchRequestDTO(BaseModel):
    query: Optional[str] = ""
    rfc_text: Optional[str] = ""
    url: Optional[str] = ""
    context: Optional[str] = ""
