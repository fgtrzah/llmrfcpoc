import re
import requests
from typing import Any
from rfcllm.config.settings import DTEP, RFCEP
from rfcllm.core.LLMController import LLMController
from rfcllm.dto.SearchRequestDTO import SearchRequestDTO
from rfcllm.services.RFCService import retriever

llmc = LLMController()


def search(app: Any):
    @app.post("/search/query/ietf")
    async def search_ietf(search: SearchRequestDTO):
        search_as_dict = search.model_dump()
        query = search_as_dict["query"]
        if not query:
            return {"error": "Malformed search query"}
        res = retriever.retrieve_search_rfceietf(query=query)
        return {"results": res}

    @app.post("/search/rfc")
    async def search_rfc(
        search: SearchRequestDTO,
    ):
        rfcid = search.dict()["query"]
        prefix = rfcid[:3]
        id = rfcid[3:].lstrip("0")
        return {
            "result": requests.get(f"{RFCEP}{(prefix + id).lower()}.txt").text,
        }

    @app.post("/search/rfc/meta")
    async def search_rfc_meta(search: SearchRequestDTO):
        search_as_dict = search.model_dump()
        text = requests.get(search_as_dict["context"]).text
        context = search_as_dict["context"]
        chronology = llmc.extract_chronology(**{"context": context})
        return {
            "refs": llmc.extract_sprawl(**{"context": context}),
            "chronology": chronology,
        }

    @app.post("/search/query/document")
    async def search_query_document(search: SearchRequestDTO):
        res = requests.get(
            f"{DTEP}api/v1/doc/document/?name__contains={search.query}&abstract__contains={search.query}&format=json&limit=1200"
        ).json()
        return {"result": res}

    return app
