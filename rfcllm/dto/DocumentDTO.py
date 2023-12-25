from dataclasses import dataclass
from typing import Optional

from flask import json

from rfcllm.dto.DocumentMetaDTO import DocumentMetaDTO


@dataclass
class DocumentDTO:
    page_content: Optional[str] = ""
    metadata: Optional[DocumentMetaDTO] = None

    def toJSON(self):
        return {
            "page_content": self.page_content,
            "metadata": json.dumps(self.metadata or {}),
        }
