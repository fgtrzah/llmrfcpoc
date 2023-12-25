from pydantic import BaseModel


class SearchRequestDTO(BaseModel):
    query: str
