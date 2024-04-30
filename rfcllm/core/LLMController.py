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
import json
import requests

from rfcllm.core.Prompter import prompter
from rfcllm.dto.DocumentMetaDTO import DocumentMetaDTO
from rfcllm.services.Llama2Service import Llama2Service
from rfcllm.services.OAIService import OAIService
from rfcllm.utils.extractors import convert_message_list_to_text
from rfcllm.utils.validators import is_url

oaisvc = OAIService()
llama2svc = Llama2Service()


class LLMController(object):
    def __init__(self) -> None:
        pass

    def invoke_combined(self):
        pass

    def extract_chronology(self, **kwargs):
        print(kwargs)
        context = kwargs.get("context", "")
        url = "" if not is_url(context) else context
        ref_text_meta = (
            DocumentMetaDTO(**requests.get(url.replace("txt", "json")).json()) or ""
        )
        p = prompter.construct_prompt(
            "Can you quote the Table Of Contents and provide padding around your quote to drive emphasis?",
            ref_text_meta,
        )
        ctx = requests.get(url=url).text
        messages = prompter.construct_message(p, ctx.split("[Page "))
        completions = oaisvc.client.chat.completions.create(
            model="gpt-4-1106-preview", messages=messages, temperature=1
        )
        completions = completions.choices[0].message.content.split("\n")
        completions = [c for c in completions if c]
        print(completions)
        return completions

    def invoke_single(self, **kwargs):
        invocation_filter = kwargs.get("invocation_filter")
        res = []

        # TODO: convert to infamous cmd map
        if invocation_filter == "llama2":
            res = self.llama2_qa_contigious(**kwargs)
        elif invocation_filter == "mistral":
            res = self.mistral_qa_contigious(**kwargs)
        else:
            if kwargs.get("stream"):
                res = self.oai_qa_stream(**kwargs)
            else:
                res = self.oai_qa_contigious(**kwargs)
            return res

        return res

    def mistral_qa_contigious(self, **kwargs):
        context = kwargs.get("context", "")
        query = kwargs.get("query", "")
        url = "" if not is_url(context) else context
        ref_text_meta = (
            DocumentMetaDTO(**requests.get(url.replace("txt", "json")).json()) or ""
        )
        p = prompter.construct_prompt(query, ref_text_meta)
        ctx = requests.get(url=url).text
        messages = prompter.construct_message(p, ctx.split("[Page"))
        completions = llama2svc.client.completions.create(
            model="mistralai/Mixtral-8x22B-Instruct-v0.1",
            prompt=convert_message_list_to_text(messages),
        )
        return completions

    def llama2_qa_contigious(self, **kwargs):
        context = kwargs.get("context", "")
        query = kwargs.get("query", "")
        url = "" if not is_url(context) else context
        ref_text_meta = (
            DocumentMetaDTO(**requests.get(url.replace("txt", "json")).json()) or ""
        )
        p = prompter.construct_prompt(query, ref_text_meta)
        ctx = requests.get(url=url).text
        messages = prompter.construct_message(p, ctx.split("[Page"))
        print(json.dumps(messages, indent=2))
        condensed_context = oaisvc.client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages,
        ).choices
        condensed_context = [ch.message for ch in condensed_context]
        completions = llama2svc.client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-8B-Instruct", messages=condensed_context
        )
        return completions

    def oai_qa_stream(self, **kwargs):
        context = kwargs.get("context", "")
        query = kwargs.get("query", "")
        url = "" if not is_url(context) else context
        ref_text_meta = (
            DocumentMetaDTO(**requests.get(url.replace("txt", "json")).json()) or ""
        )
        p = prompter.construct_prompt(query, ref_text_meta)
        ctx = requests.get(url=url).text
        messages = prompter.construct_message(p, ctx.split("[Page"))
        print(json.dumps(messages, indent=2))
        completions = oaisvc.client.chat.completions.create(
            model="gpt-4-1106-preview",
            stream=True,
            messages=messages,
            temperature=1,
        )
        return completions

    def oai_qa_contigious(self, **kwargs):
        context = kwargs.get("context", "")
        query = kwargs.get("query", "")
        url = "" if not is_url(context) else context
        ref_text_meta = (
            DocumentMetaDTO(**requests.get(url.replace("txt", "json")).json()) or ""
        )
        p = prompter.construct_prompt(query, ref_text_meta)
        ctx = requests.get(url=url).text
        messages = prompter.construct_message(p, ctx.split("[Page"))
        print(json.dumps(messages, indent=2))
        completions = oaisvc.client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages,
        )
        return completions

    def cohere(self):
        pass

    def mistral(self):
        pass
