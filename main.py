import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from rfcllm.core import Prompter as prompter
from rfcllm.evals.eval_routes import eval_routes
from rfcllm.group.routes import group
from rfcllm.iam.routes import iam
from rfcllm.qa.routes import qa
from rfcllm.search.routes import search

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

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

# deprecating
app = iam(app)
app = search(app)
app = group(app)
app = qa(app)
app = eval_routes(app)

# current
if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        ssl_keyfile="./fgtrz.com+3-key.pem",
        ssl_certfile="./fgtrz.com+3.pem",
        host="127.0.0.1", 
        port=8080,
        reload=True
    )
