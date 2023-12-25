from pydantic import BaseModel


class InquiryDTO(BaseModel):
    query: str
    context: str