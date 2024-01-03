from typing import Annotated, Any
import base64, os, requests
from fastapi import Depends, FastAPI
from flask import jsonify
from rfcllm.config.settings import DTEP 
from rfcllm.core import Prompter as prompter, RFCRetriever as rfcretriever
from rfcllm.dto.DocumentMetaDTO import DocumentMetaDTO
from rfcllm.dto.InquiryDTO import InquiryDTO
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from rfcllm.group.routes import group
from rfcllm.utils.validators import is_url
from rfcllm.iam.routes import iam
from rfcllm.search.routes import search
from rfcllm.iam.dto import User 
from rfcllm.iam.utils import get_current_active_user 

OPENAI_API_KEY = base64.b64decode(os.environ.get("OPENAI_API_KEY", ""))
client = OpenAI(
    api_key=base64.b64decode(
        "c2stUjRZRktpSFJjM0VwMEFVQ0R5bnZUM0JsYmtGSmpYeVE3OVdxYllFc1BMb29Lb1RH"
    ).decode()
)
prompter = prompter.Prompter()
app = FastAPI()
origins = ["http://localhost:5174"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = iam(app)
app = search(app)
app = group(app)
 

@app.post("/qa/single/contigious")
async def qa_single_contigious(
    current_user: Annotated[User, Depends(get_current_active_user)], inquiry: InquiryDTO
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
