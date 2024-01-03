import base64, os
from fastapi import FastAPI
from rfcllm.core import Prompter as prompter
from fastapi.middleware.cors import CORSMiddleware
from rfcllm.group.routes import group
from rfcllm.iam.routes import iam
from rfcllm.qa.routes import qa
from rfcllm.search.routes import search

OPENAI_API_KEY = base64.b64decode(os.environ.get("OPENAI_API_KEY", ""))

prompter = prompter.Prompter()
app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = iam(app)
app = search(app)
app = group(app)
app = qa(app)
