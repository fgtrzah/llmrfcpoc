import requests
from typing import Annotated, Any
from rfcllm.config.settings import DTEP, RFCEP
from fastapi import Depends
from rfcllm.iam.dto import User
from rfcllm.iam.utils import get_current_active_user
from rfcllm.search.dto import SearchRequestDTO
from rfcllm.services.RFCService import retriever


def search(app: Any):
    @app.post("/search/query/ietf")
    async def search_ietf(search: SearchRequestDTO):
        print(search)
        res = retriever.retrieve_search_rfceietf(query=search.query)
        return {"results": res}

    @app.post("/search/rfc")
    async def search_rfc(
        current_user: Annotated[User, Depends(get_current_active_user)],
        search: SearchRequestDTO,
    ):
        rfcid = search.dict()["query"]
        return {
            "result": requests.get(f"{RFCEP}{rfcid}.txt").text,
            "current_user": current_user.email,
        }

    @app.post("/search/query/document")
    async def search_query_document(search: SearchRequestDTO):
        res = requests.get(f"{DTEP}api/v1/doc/document/{search.query}").json()
        return {
            "result": res,
        }

    return app
