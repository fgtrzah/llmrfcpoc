from typing import Any
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
        invocation_filter = inquiry_as_dict["invocation_filter"]

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
                "results": res,
                "query": query,
                "context": context,
            }
        except requests.exceptions.RequestException as e:
            return {"message": {"error": e}}

    from fastapi.responses import StreamingResponse

    @app.post("/qa/single/stream")
    async def qa_single_stream(inquiry: InquiryDTO):
        inquiry_as_dic = inquiry.model_dump()
        query = inquiry_as_dic["query"]
        context = inquiry_as_dic["context"]

        if not query or not context:
            return {"message": "Malformed completion request"}, 401

        try:
            url = "" if not is_url(context) else context
            ref_text_meta = (
                DocumentMetaDTO(**requests.get(url.replace("txt", "json")).json()) or ""
            )
            p = prompter.construct_prompt(query, ref_text_meta)
            ctx = requests.get(url=url).text
            messages: Any = prompter.construct_message(p, ctx.split("[Page"))
            completions = oaisvc.client.chat.completions.create(
                model="gpt-4-1106-preview",
                stream=True,
                messages=messages,
                temperature=0,
            )

            async def generate():
                for chunk in completions:
                    resp_json = chunk.model_dump_json()
                    yield "data: " + resp_json + "\n\n"
                yield ""

            return StreamingResponse(generate(), media_type="text/event-stream")
        except requests.RequestException as e:
            return {"error": e.__str__()}

    @app.post("/qa/evals/stream")
    async def qa_evals_stream(inquiry: dict):
        try:
            client = oaisvc.client
            stream = await client.chat.completions.create(
                messages=inquiry["messages"],
                model="gpt-3.5-turbo",
                stream=True,
            )

            async def generator():
                async for chunk in stream:
                    yield chunk.choices[0].delta.content or ""

            r = generator()
            return StreamingResponse(r, media_type="text/event-stream")
        except requests.RequestException as e:
            return {"error": e.__str__()}

    return app
