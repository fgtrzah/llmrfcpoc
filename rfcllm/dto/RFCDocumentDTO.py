from dataclasses import dataclass
import json
from typing import Optional

from rfcllm.dto.RFCDocumentMetaDTO import RFCDocumentMetaDTO


@dataclass
class RFCDocumentDTO:
    page_content: Optional[str] = ""
    metadata: Optional[RFCDocumentMetaDTO] = None

    def toJSON(self):
        return {
            "page_content": self.page_content,
            "metadata": json.dumps(self.metadata or {}),
        }
