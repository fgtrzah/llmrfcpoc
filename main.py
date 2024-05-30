import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from rfcllm.core import Prompter as prompter
from rfcllm.datasets.routes import datasets
from rfcllm.evals.routes import evals
from rfcllm.group.routes import group
from rfcllm.iam.routes import iam
from rfcllm.qa.routes import qa
from rfcllm.search.routes import search

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
description = """

RFCINDEX API is the underlying platform api powering the
research around RFCINDEX. The API features a spectrum of
offerings such as document search, authentication, data
introspection, llm utilities, and cqrs which facilitates
platform needs.

Some verticals or domains worth explicitly noting:\n
    search -> global omnisearch over rfc documents and meta data
    qa -> closed doc contextual qa
    evals -> evaluations of emerging research concepts around gen ai / general rapid prototyping workbench
"""

prompter = prompter.Prompter()
app = FastAPI(
    title="RFCINDEX API",
    openapi_url="/api/v1/openapi.json",
    description=description,
    include_in_schema=True,
)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# deprecating
app = iam(app)
app = search(app)
app = group(app)
app = qa(app)
app = evals(app)
app = datasets(app)

# current
if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        ssl_keyfile="./fgtrz.com+3-key.pem",
        ssl_certfile="./fgtrz.com+3.pem",
        host="127.0.0.1",
        port=8080,
        reload=True,
    )
