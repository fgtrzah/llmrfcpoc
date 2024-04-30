from typing import Any
from fastapi.responses import StreamingResponse
import requests
from rfcllm.config.settings import INVOCATION_MODES
from rfcllm.core.LLMController import LLMController
from rfcllm.core.Prompter import prompter
from rfcllm.dto.DocumentMetaDTO import DocumentMetaDTO
from rfcllm.dto.InquiryDTO import InquiryDTO

from rfcllm.services.OAIService import OAIService
from rfcllm.utils.validators import is_url

oaisvc = OAIService()
llmc = LLMController()


def qa(app: Any):
    @app.post("/qa/single/contigious")
    async def qa_single_contigious(inquiry: InquiryDTO):
        inquiry_as_dict = inquiry.model_dump()
        query = inquiry_as_dict["query"]
        context = inquiry_as_dict["context"]
        invocation_mode = (
            inquiry_as_dict["invocation_mode"] or INVOCATION_MODES["SINGLE"]
        )

        if not query or not context:
            return {"message": "Malformed completion request"}, 401

        res = []

        try:
            if invocation_mode == INVOCATION_MODES["SINGLE"]:
                completion = llmc.invoke_single(**inquiry_as_dict)
            elif invocation_mode == INVOCATION_MODES["COMBINED"]:
                completion = llmc.invoke_combined(**inquiry_as_dict)
            else:
                return {
                    "message": "Malformed completion request, please troubleshoot invocation parameters"
                }, 401

            res.append(completion)

            return {
                "completion": completion,
                "query": query,
                "context": context
            }
        except requests.exceptions.RequestException as e:
            return {"message": {"error": e}}

    @app.post("/qa/evals/stream")
    async def qa_evals_stream(inquiry: dict):
        try:
            client = oaisvc.client
            stream = client.chat.completions.create(
                messages=inquiry["messages"], model="gpt-3.5-turbo", stream=True
            )

            async def generator():
                for chunk in stream:
                    yield chunk.choices[0].delta.content or ""

            r = generator()
            return StreamingResponse(r, media_type="text/event-stream")
        except requests.RequestException as e:
            return {"error": e.__str__()}

    return app
