import json
from typing import Any, AsyncGenerator, NoReturn
import requests
from fastapi import WebSocket
from rfcllm.core.Prompter import prompter
from rfcllm.dto.DocumentMetaDTO import DocumentMetaDTO
from rfcllm.dto.InquiryDTO import InquiryDTO

from rfcllm.services.OAIService import OAIService
from rfcllm.utils.validators import is_url

oaisvc = OAIService()


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
            completion = oaisvc.client.chat.completions.create(
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

    @app.websocket("/ws")
    async def ws(websocket: WebSocket):
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")

    @app.websocket("/qa/single/ws")
    async def websocket_endpoint(websocket: WebSocket) -> NoReturn:
        """
        Websocket for AI responses
        """
        await websocket.accept()
        
        while True:
            message = await websocket.receive_text()
            print(message)
            async for text in get_ai_response(message):
                await websocket.send_text(text)

    async def get_ai_response(message: str) -> AsyncGenerator[str, None]:
        """
        OpenAI Response
        """

        response = await oaisvc.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant, skilled in explaining "
                        "complex concepts in simple terms."
                    ),
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
            stream=True,
        )

        all_content = ""
        async for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                all_content += content
                yield all_content

    from fastapi.responses import StreamingResponse
    from typing import Iterable

    # Route to handle SSE events and return users
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
            messages: Any = prompter.construct_message(p, ctx.split('[Page'))
            print(messages)
            completions = oaisvc.client.chat.completions.create(
                model="gpt-4-1106-preview",
                stream=True,
                messages=messages
            )

            async def generate():
                for user in completions:
                    resp_json = user.model_dump_json()
                    yield resp_json
                yield '{}' 

            return StreamingResponse(generate(), media_type="text/event-stream")
        except requests.RequestException as e:
            print(e)
            return {'error': e.__str__()}

    return app
