```python
# two intermediate snippets which we'll stow for later reference
def get_openai_generator(prompt: str):
    openai_stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        stream=True,
    )
    for event in openai_stream:
        if "content" in event["choices"][0].delta:
            current_response = event["choices"][0].delta.content
            yield "data: " + current_response + "\n\n"

@app.get('/stream')
async def stream():
    return StreamingResponse(get_openai_generator(prompt), media_type='text/event-stream')

@qa.post("/single")
@authorized
def single():
    req_data = request.get_json()
    query, context = req_data["query"]
    ctx = req_data["context"]
    url = ctx if is_url(ctx) else ""

    try:
        ref_text_meta = (
            DocumentMetaDTO(**requests.get(url.replace("txt", "json")).json())
            or ""
        )
        p = prompter.construct_prompt(q, ref_text_meta)
        ctx = RFCRetriever(url=url.replace('txt', 'html')).load()
        response = oaiservice.client.chat.completions.create(
            model='gpt-4-1106-preview',
            messages=prompter.construct_message(p, ctx),
        )

        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "message": jsonify({'error': e})
        }
```