from openai import OpenAI
from typing import Any
from rfcllm.config.settings import LLAMA2API_KEY, LLAMA2ENDPOINT, OPENAI_API_KEY


class Llama2Service:
    api_key: str
    client: Any
    completion_model: str
    embedding_model: str
    base_url: str

    def __init__(self):
        self.client = OpenAI(base_url=LLAMA2ENDPOINT, api_key=LLAMA2API_KEY)

    async def get_completion_stream(self, **kwargs: Any):
        completion = self.client.chat.completions.create(
            model=kwargs.get("model") or "meta-llama/Llama-2-70b-chat-hf",
            prompt=kwargs.get("prompt"),
            temperature=kwargs.get("temperature") or 0.1,
        )
        return completion
