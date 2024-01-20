import base64
from typing import Any
from openai import OpenAI


class OAIService:
    api_key: str
    client: Any
    completion_model: str
    embedding_model: str

    def __init__(self):
        self.client = OpenAI(
            api_key=base64.b64decode(
                "c2stUjRZRktpSFJjM0VwMEFVQ0R5bnZUM0JsYmtGSmpYeVE3OVdxYllFc1BMb29Lb1RH"
            ).decode()
        )

    async def get_completion_stream(self, **kwargs: Any):
        completions = await self.client.chat.completions.create(
            messages=kwargs.get("messages"),
            model="gpt-3.5-turbo",
        )
        return completions
