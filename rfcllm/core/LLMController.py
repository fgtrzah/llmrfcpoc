"""
Synopsis: 
    This class acts as the collocation of everything 
    related to LLMS, due to exploring multi-modal poly-
    provider use-cases (e.g. joining responses from 
    cohere + openai + whatever else, or switching 
    from response to response), having one 
    central place where the api routing code
    talks to llm(s) felt better than cramming 
    bespoke logic inside every handler
"""

"""
- have a dict of model names
- req provides model id for mono
- req provides model ids for
  composition
"""
import requests

from rfcllm.core.Prompter import prompter
from rfcllm.dto.DocumentMetaDTO import DocumentMetaDTO
from rfcllm.services.OAIService import OAIService
from rfcllm.utils.validators import is_url

oaisvc = OAIService()


class LLMController(object):
    def __init__(self) -> None:
        self.llms = {"oai": self.oai}

    def invoke_combined(self):
        pass

    def invoke_single(self, **kwargs):
        print(kwargs)
        invocation_filter = kwargs.get("invocation_filter")
        res = []
        if invocation_filter == "oai":
            res = self.oai(**kwargs)
            return res
        return res

    def oai(self, **kwargs):
        context = kwargs.get("context", "")
        query = kwargs.get("query", "")
        url = "" if not is_url(context) else context
        ref_text_meta = (
            DocumentMetaDTO(**requests.get(url.replace("txt", "json")).json()) or ""
        )
        p = prompter.construct_prompt(query, ref_text_meta)
        ctx = requests.get(url=url).text
        message = prompter.construct_message(p, ctx.split("[Page"))
        completion = oaisvc.client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=message,
        )
        return completion

    def cohere(self):
        pass

    def mistral(self):
        pass
