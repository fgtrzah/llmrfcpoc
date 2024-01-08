import base64, time, asyncio, json
from typing import Annotated, Any
from fastapi import Depends 
from fastapi.responses import StreamingResponse 
from openai import OpenAI
import requests
from flask import jsonify
import rfcllm.core.RFCRetriever as rfcretriever
from rfcllm.core.Prompter import prompter
from rfcllm.dto.DocumentMetaDTO import DocumentMetaDTO
from rfcllm.dto.InquiryDTO import InquiryDTO

from rfcllm.iam.dto import User
from rfcllm.iam.utils import get_current_active_user
from rfcllm.utils.validators import is_url

client = OpenAI(
    api_key=base64.b64decode(
        "c2stUjRZRktpSFJjM0VwMEFVQ0R5bnZUM0JsYmtGSmpYeVE3OVdxYllFc1BMb29Lb1RH"
    ).decode()
)


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
            completion = client.chat.completions.create(
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
   
    async def generator():
        for i in range(10):
            yield "some streamed data"
            await asyncio.sleep(1) # sleep one second

    def fake_data_streamer():
        for i in range(10):
            yield json.dumps({"event_id": i, "data": "some random data", "is_last_event": i == 9}) + '\n'

            time.sleep(0.5)

    @app.get("/")
    async def root():
        print("Received a request on /")
        return {"message": "Hello World"}
    @app.get('/stream')
    async def main():
        return StreamingResponse(fake_data_streamer(), media_type='application/x-ndjson')

    return app
