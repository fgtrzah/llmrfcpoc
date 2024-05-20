from dataclasses import dataclass
from typing import Any, Optional
from pydantic import BaseModel


class ResourceDTO(BaseModel):
    resourcetype: str
    id: str
    attributes: Optional[Any] = {}
    links: Optional[Any] = {}
    relationships: Optional[Any] = {}
    meta: Optional[Any] = {}
