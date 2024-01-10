import base64, time, asyncio, json
from typing import Annotated, Any
from fastapi import Depends, Header, applications 
from fastapi.responses import StreamingResponse
from httpx import Headers, request 
from openai import OpenAI
import requests
from flask import jsonify
import rfcllm.core.RFCRetriever as rfcretriever
from rfcllm.core.Prompter import prompter
from rfcllm.dto.DocumentMetaDTO import DocumentMetaDTO
from rfcllm.dto.InquiryDTO import InquiryDTO

from rfcllm.iam.dto import User
from rfcllm.iam.utils import get_current_active_user
from rfcllm.services.OAIService import OAIService
from rfcllm.utils.validators import is_url

client = OAIService()


def qa(app: Any):
    @app.post("/qa/single/contigious")
    async def qa_single_contigious(
        current_user: Annotated[User, Depends(get_current_active_user)],
        inquiry: InquiryDTO,
    ):
        # Example of an OpenAI ChatCompletion request
        # https://platform.openai.com/docs/guides/chat
        inquiry_as_dic: Any = inquiry.dict()
        query = inquiry_as_dic["query"]
        context = inquiry_as_dic["context"]

        if not query or not context:
            return {"message": "Malformed completion request"}, 401

        res = []
        try:
            # construct the whole long prompt by splitting the contents
            # of the rfc document present at the provided url
            url = "" if not is_url(context) else context
            ref_text_meta = (
                DocumentMetaDTO(**requests.get(url.replace("txt", "json")).json()) or ""
            )
            p = prompter.construct_prompt(query, ref_text_meta)
            ctx = rfcretriever.RFCRetriever(url=url.replace("txt", "html")).load()
            message: Any = prompter.construct_message(p, ctx)
            # send a ChatCompletion request to count to 100
            completion = client.client.completions.create(
                model="gpt-4-1106-preview",
                messages=message,
            )

            res.append(completion)

            return {
                "completion": completion,
                "results": res,
                "query": query,
                "context": context,
                "current_user": current_user,
            }
        except requests.exceptions.RequestException as e:
            return {"message": jsonify({"error": e})}
   
    def fake_data_streamer(c):
        for i in range(10):
            yield json.dumps(c) + '\n'

    @app.post('/qa/single/stream')
    async def qa_single_stream(
        current_user: Annotated[User, Depends(get_current_active_user)],
        inquiry: InquiryDTO,
    ):
        inquiry_as_dic: Any = inquiry.dict()
        query = inquiry_as_dic["query"]
        context = inquiry_as_dic["context"]

        if not query or not context:
            return {"message": "Malformed completion request"}, 401

        res = []
        try:
            # construct the whole long prompt by splitting the contents
            # of the rfc document present at the provided url
            url = "" if not is_url(context) else context
            ref_text_meta = (
                DocumentMetaDTO(**requests.get(url.replace("txt", "json")).json()) or ""
            )
            p = prompter.construct_prompt(query, ref_text_meta)
            ctx = rfcretriever.RFCRetriever(url=url.replace("txt", "html")).load()
            message: Any = prompter.construct_message(p, ctx)
            # send a ChatCompletion request to count to 100

            completions = await requests.post(
                'https://api.openai.com/v1/chat/completions', 
                json={
                    "model": "gpt-4-1106-preview",
                    "messages": message,
                    "stream": True
                },
                headers=jsonify({
                    "Authorization": f'Bearer {base64.b64decode("c2stUjRZRktpSFJjM0VwMEFVQ0R5bnZUM0JsYmtGSmpYeVE3OVdxYllFc1BMb29Lb1RH").decode()}',
                    "Content-Type": "applications/json"
                })
            ).json()

            return StreamingResponse(fake_data_streamer(completions), media_type='application/x-ndjson')
        except ValueError as e:
             return {"res":"no"}

    return app
