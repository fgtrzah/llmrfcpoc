from typing import Any
import requests
from rfcllm.core.Prompter import prompter
from rfcllm.dto.DocumentMetaDTO import DocumentMetaDTO
from rfcllm.dto.InquiryDTO import InquiryDTO

from rfcllm.services.OAIService import OAIService
from rfcllm.utils.validators import is_url

oaisvc = OAIService()


def qa(app: Any):
    @app.post("/qa/single/contigious")
    async def qa_single_contigious(inquiry: InquiryDTO):
        inquiry_as_dic: Any = inquiry.dict()
        query = inquiry_as_dic["query"]
        context = inquiry_as_dic["context"]

        if not query or not context:
            return {"message": "Malformed completion request"}, 401

        res = []
        try:
            url = "" if not is_url(context) else context
            ref_text_meta = (
                DocumentMetaDTO(**requests.get(url.replace("txt", "json")).json()) or ""
            )
            p = prompter.construct_prompt(query, ref_text_meta)
            ctx = requests.get(url=url).text
            message: Any = prompter.construct_message(p, ctx.split("[Page"))
            completion = oaisvc.client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=message,
            )

            res.append(completion)

            # TODO: opt into DTOs for this sort of stuff
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
    async def extract(inquiry: InquiryDTO):
        inquiry_as_dic: Any = inquiry.dict()
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

    return app
