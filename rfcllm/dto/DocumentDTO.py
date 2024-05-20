from dataclasses import dataclass
from typing import Any, Optional, Union
from pydantic import BaseModel


class DocumentDTO(BaseModel):
    data: Any
    errors: Optional[dict] = {}
    meta: Optional[dict] = {}
