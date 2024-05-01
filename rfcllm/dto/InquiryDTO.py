from typing import Any, Optional
from pydantic import BaseModel

from rfcllm.config.settings import INVOCATION_MODES


class InquiryDTO(BaseModel):
    url: Optional[Any] = None
    query: Optional[Any] = None
    context: Optional[Any] = None
    invocation_mode: Optional[str] = INVOCATION_MODES["SINGLE"]
    invocation_filter: Optional[str] = "oai"
    messages: Optional[Any] = None
