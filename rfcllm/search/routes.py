import re
import requests
from typing import Any
from rfcllm.config.settings import DTEP, RFCEP
from rfcllm.core.LLMController import LLMController
from rfcllm.dto.SearchRequestDTO import SearchRequestDTO
from rfcllm.services.RFCService import retriever
from rfcllm.utils.extractors import extract_urls
from rfcllm.utils.validators import is_url, num_tokens_from_string

llmc = LLMController()


def search(app: Any):
    @app.post("/search/query/ietf")
    async def search_ietf(search: SearchRequestDTO):
        search_as_dict = search.model_dump()
        query = search_as_dict["query"]
        if not query:
            return {"error": "Malformed search query"}
        res: Any = retriever.retrieve_search_rfceietf(query=query)
        return {
            "data": {"type": "SearchQueryIETFResponse", "attributes": {"results": res}}
        }

    @app.post("/search/rfc")
    async def search_rfc(
        search: SearchRequestDTO,
    ):
        rfcid = search.model_dump()["query"]
        prefix = rfcid[:3]
        id = rfcid[3:].lstrip("0")

        return {
            "data": {
                "type": "SearchQueryIETFResponse",
                "attributes": {
                    "result": requests.get(f"{RFCEP}{(prefix + id).lower()}.txt").text,
                    "html": requests.get(f"{RFCEP}{(prefix + id).lower()}.html").text,
                    "xml": requests.get(f"{RFCEP}{(prefix + id).lower()}.xml").text,
                },
            }
        }

    @app.post("/search/rfc/meta")
    async def search_rfc_meta(search: SearchRequestDTO):
        search_as_dict = search.model_dump()
        context = search_as_dict.get("context", "")
        if not context or not is_url(context):
            return {"refs": [], "chronology": []}
        url = "" if not is_url(context) else context
        context = requests.get(url=url).text
        chronology = llmc.extract_chronology(**{"context": context})

        return {
            "data": {
                "type": "SearchQueryIETFResponse",
                "attributes": {"chronology": chronology, "refs": extract_urls(context)},
            }
        }

    @app.post("/search/query/document")
    async def search_query_document(search: SearchRequestDTO):
        res = requests.get(
            f"{DTEP}api/v1/doc/document/?name__contains={search.query}&abstract__contains={search.query}&format=json&limit=1200"
        ).json()
        return {"result": res}

    return app
