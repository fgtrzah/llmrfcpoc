from typing import Any
from openai import AsyncOpenAI


class OAIService:
    api_key: str
    client: Any
    completion_model: str
    embedding_model: str

    def __init__(self):
        self.client = AsyncOpenAI(
            # This is the default and can be omitted
            api_key=self.api_key
        )

    async def get_completion_stream(self, **kwargs: Any):
        completions = await self.client.chat.completions.create(
            messages=kwargs.get('messages'),
            model="gpt-3.5-turbo",
        )
        return completions
