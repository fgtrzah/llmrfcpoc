from dataclasses import dataclass
from typing import Any
from typing import List
from typing import Optional


@dataclass
class DocumentMetaDTO:
    errata_url: None
    page_count: Optional[int] = None
    draft: Optional[str] = None
    doc_id: Optional[str] = None
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    format: Optional[List[str]] = None
    pub_status: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None
    abstract: Optional[str] = None
    pub_date: Optional[str] = None
    keywords: Optional[List[str]] = None
    obsoletes: Optional[List[Any]] = None
    obsoleted_by: Optional[List[Any]] = None
    updates: Optional[List[Any]] = None
    updated_by: Optional[List[str]] = None
    see_also: Optional[List[Any]] = None
    doi: Optional[str] = None
