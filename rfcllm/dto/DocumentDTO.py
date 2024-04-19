from dataclasses import dataclass
import json
from typing import Optional

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
