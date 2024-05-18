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
from rfcllm.utils.validators import is_url, num_tokens_from_messages

oaisvc = OAIService()
llama2svc = Llama2Service()


class LLMController(object):
    def __init__(self) -> None:
        pass

    def invoke_combined(self):
        pass

    def extract_sprawl(self, **kwargs):
        context = kwargs.get("context", "")
        p = prompter.construct_prompt(
            "Can you take every external url mentioned in this RFC and gather it into a bulletted list?",
            context,
        )
        messages = prompter.construct_message(p, context.split("[Page "))
        completions = oaisvc.client.chat.completions.create(
            model="gpt-3.5-turbo-16k", messages=messages, temperature=1
        )
        completions = completions.choices[0].message.content.split("\n")
        completions = [c for c in completions if c]
        return completions

    def extract_chronology(self, **kwargs):
        context = kwargs.get("context", "") 
        p = prompter.construct_prompt(
            "Can you quote the Table Of Contents and provide padding around your quote to drive emphasis?",
            context,
        )
        messages = prompter.construct_message(p, context.split("[Page "))
        completions = oaisvc.client.chat.completions.create(
            model="gpt-4-turbo-2024-04-09", messages=messages, temperature=1, max_tokens=2096
        )
        completions = completions.choices[0].message.content.split("\n")
        completions = [c for c in completions if c]
        return completions

    def invoke_single(self, **kwargs):
        invocation_filter = kwargs.get("invocation_filter")
        res = []

        # fix toxicity for llama2 - its really abrasive
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
            model="gpt-4-turbo-2024-04-09",
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
        completions = oaisvc.client.chat.completions.create(
            model="gpt-4-turbo-2024-04-09",
            stream=True,
            messages=messages,
            temperature=1,
        )
        return completions

    def oai_qa_contigious(self, **kwargs):
        context = kwargs.get("context", "")
        query = kwargs.get("query", "")
        url = "" if not is_url(context) else context
        ctx = requests.get(url=url).text
        p = prompter.construct_prompt(query, ctx)
        messages = prompter.construct_message(p, ctx.split("[Page"))
        completion = oaisvc.client.chat.completions.create(
            model="gpt-4-turbo-2024-04-09",
            messages=messages,
        )
        return completion

    def cohere(self):
        pass

    def mistral(self):
        pass
