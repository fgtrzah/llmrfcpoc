from typing import Any
import requests
from rfcllm.core.Prompter import prompter
from rfcllm.dto.DocumentMetaDTO import DocumentMetaDTO
from rfcllm.dto.InquiryDTO import InquiryDTO

from rfcllm.services.OAIService import OAIService
from rfcllm.utils.validators import is_url

client = OAIService()


def qa(app: Any):
    @app.post('/qa/single/contigious')
    async def qa_single_contigious(inquiry: InquiryDTO):
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
            ctx = requests.get(url=url).text
            message: Any = prompter.construct_message(p, ctx.split('[Page'))
            # send a ChatCompletion request to count to 100
            completion = client.client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=message,
            )

            res.append(completion)

            return {
                "completion": completion,
                "results": res, 
                "query": query,
                "context": context
            }
        except requests.exceptions.RequestException as e:
            return {"message": {"error": e}}

    return app
