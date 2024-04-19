from typing import Optional
from pydantic import BaseModel

from rfcllm.config.settings import INVOCATION_MODES


class InquiryDTO(BaseModel):
    query: str
    context: str
    invocation_mode: Optional[str] = INVOCATION_MODES["SINGLE"]
    invocation_filter: Optional[str] = "oai"
