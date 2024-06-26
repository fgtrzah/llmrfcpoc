"""
Synopsis: 
    Glues all the LLM invocation and routing
    between llms.
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
from rfcllm.dto.RFCDocumentMetaDTO import RFCDocumentMetaDTO
from rfcllm.services.Llama2Service import Llama2Service
from rfcllm.services.OAIService import OAIService
from rfcllm.utils.extractors import (
    convert_message_list_to_text,
    remove_blank_and_footer_lines,
)
from rfcllm.utils.validators import is_url

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
            model="gpt-4-turbo-2024-04-09",
            messages=messages,
            temperature=1,
            max_tokens=2096,
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
            RFCDocumentMetaDTO(**requests.get(url.replace("txt", "json")).json()) or ""
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
            RFCDocumentMetaDTO(**requests.get(url.replace("txt", "json")).json()) or ""
        )
        p = prompter.construct_prompt(query, ref_text_meta)
        ctx = requests.get(url=url).text
        messages = prompter.construct_message(p, ctx.split("[Page"))
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
            RFCDocumentMetaDTO(**requests.get(url.replace("txt", "json")).json()) or ""
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

        # refactor into utility
        ctx = remove_blank_and_footer_lines(ctx)
        p = prompter.construct_prompt(query, ctx)
        delim = url.split("/")[-1].split(".")[0]
        delim = delim[:3].upper() + " " + delim[3:]
        ctx = ctx.split(delim)

        messages = prompter.construct_message(p, ctx)
        completion = oaisvc.client.chat.completions.create(
            model="gpt-4-turbo-2024-04-09",
            messages=messages,
        )
        return completion

    def cohere(self):
        pass

    def mistral(self):
        pass

    def oai_qa_feedforward(self, **kwargs):
        # ... query extraction step ...
        url = kwargs.get("url", "")

        if not is_url(url):
            return {
                "message": "Malformed completion request - please provide valid context doc url"
            }, 401

        # ... llm input construction step ...
        ctx = requests.get(url=url).text
        ctx = remove_blank_and_footer_lines(ctx)
        messages = prompter.construct_sysff_message(ctx)

        # ... llm invocation ...
        completions = oaisvc.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            temperature=1,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        return completions
