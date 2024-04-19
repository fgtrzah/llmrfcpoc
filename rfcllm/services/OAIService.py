from openai import OpenAI
from typing import Any
from rfcllm.config.settings import OPENAI_API_KEY


class OAIService:
    api_key: str
    client: Any
    completion_model: str
    embedding_model: str

    def __init__(self):
        print(OPENAI_API_KEY)
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    async def get_completion_stream(self, **kwargs: Any):
        completions = await self.client.chat.completions.create(
            messages=kwargs.get("messages"),
            model="gpt-3.5-turbo",
        )
        return completions
